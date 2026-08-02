from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from backend.config import config
from backend.database.models.organization import Organization, OrganizationMember
from backend.database.models.project import Project, ProjectMember
from backend.database.models.role import Permission, Role, UserRole
from backend.database.models.user import User
from backend.database.session import get_db

# Password hashing — single source of truth is passwords.py
from backend.auth.passwords import hash_password, verify_password
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

# OAuth2 schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
oauth2_auth_code = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/api/v1/auth/oauth2/authorize",
    tokenUrl="/api/v1/auth/token",
)


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    API_KEY = "api_key"


class OrgUserRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


@dataclass
class TokenPayload:
    sub: str  # user_id
    email: str
    org_id: str | None = None
    project_id: str | None = None
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    token_type: TokenType = TokenType.ACCESS
    exp: int | None = None
    iat: int | None = None
    jti: str | None = None


class AuthManager:
    def __init__(self):
        # Same fail-fast guard as jwt.py — never sign with a guessable key.
        from backend.auth.jwt import validate_secret_key

        self.secret_key = validate_secret_key(config.auth.secret_key)
        self.algorithm = config.auth.algorithm
        self.access_token_expire = timedelta(minutes=config.auth.access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=config.auth.refresh_token_expire_days)
        self.issuer = config.auth.issuer
        self.audience = config.auth.audience

    def hash_password(self, password: str) -> str:
        return hash_password(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return verify_password(plain, hashed)

    def create_access_token(
        self,
        user: User,
        org_id: str | None = None,
        project_id: str | None = None,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        now = datetime.utcnow()
        expire = datetime.utcnow() + (expires_delta or self.access_token_expire)

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "org_id": org_id,
            "project_id": project_id,
            "roles": roles or [],
            "permissions": permissions or [],
            "token_type": TokenType.ACCESS.value,
            "exp": expire,
            "iat": now,
            "iss": self.issuer,
            "aud": self.audience,
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user: User, expires_delta: timedelta | None = None) -> str:
        now = datetime.utcnow()
        expire = now + (self.refresh_token_expire or timedelta(days=7))

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "token_type": TokenType.REFRESH.value,
            "exp": expire,
            "iat": now,
            "iss": self.issuer,
            "aud": self.audience,
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
            )
            # Build TokenPayload explicitly: ``TokenPayload(**payload)`` would
            # crash on JWTManager-issued tokens (extra ``iss``/``aud``/``type``
            # claims + missing required ``email``). Map ``type`` -> ``token_type``.
            return TokenPayload(
                sub=payload.get("sub", ""),
                email=payload.get("email", ""),
                org_id=payload.get("org_id"),
                project_id=payload.get("project_id"),
                roles=payload.get("roles") or [],
                permissions=payload.get("permissions") or [],
                token_type=TokenType(
                    payload.get("token_type") or payload.get("type") or TokenType.ACCESS.value
                ),
                exp=payload.get("exp"),
                iat=payload.get("iat"),
                jti=payload.get("jti"),
            )
        except (JWTError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def verify_token(self, token: str) -> TokenPayload:
        payload = self.decode_token(token)
        if payload.token_type != TokenType.ACCESS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        return payload


# Global auth manager
auth_manager = AuthManager()


# Dependency for getting current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = auth_manager.verify_token(token)
    user = await db.get(User, payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    return user


# Organization context
async def get_current_org(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Organization:
    # Get user's default organization or first membership
    membership = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .order_by(OrganizationMember.role.desc())
        .limit(1)
    )
    membership = membership.scalar_one_or_none()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of any organization",
        )
    org = await db.get(Organization, membership.organization_id)
    if not org or not org.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization not found or inactive",
        )
    return org


# Project context
async def get_current_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Project:
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    # Check membership
    membership = await db.execute(
        select(ProjectMember).where(
            and_(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id,
            )
        )
    )
    if not membership.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this project",
        )
    return project


# Role-based access control
class PermissionChecker:
    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        org: Organization = Depends(get_current_org),
    ) -> User:
        # Get user's permissions in this org
        user_roles = await db.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                and_(
                    UserRole.user_id == current_user.id,
                    UserRole.organization_id == org.id,
                    UserRole.is_active,
                )
            )
        )
        roles = user_roles.scalars().all()

        user_permissions = set()
        for role in roles:
            for perm in role.permissions:
                user_permissions.add(f"{perm.resource}:{perm.action}")

        # Check if user has all required permissions
        missing = set(self.required_permissions) - user_permissions
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing)}",
            )

        return current_user


def require_permissions(*permissions: str) -> PermissionChecker:
    return PermissionChecker(list(permissions))


# Multi-tenancy: Row-level security
class TenantFilter:
    def __init__(self, model_class, tenant_field: str = "organization_id"):
        self.model_class = model_class
        self.tenant_field = tenant_field

    def apply(self, query, org_id: str):
        return query.where(getattr(self.model_class, self.tenant_field) == org_id)


class TenantContext:
    def __init__(self):
        self._org_id: str | None = None
        self._project_id: str | None = None

    @property
    def org_id(self) -> str | None:
        return self._org_id

    @property
    def project_id(self) -> str | None:
        return self._project_id

    def set_tenant(self, org_id: str, project_id: str | None = None):
        self._org_id = org_id
        self._project_id = project_id

    def clear(self):
        self._org_id = None
        self._project_id = None


tenant_context = TenantContext()


async def get_tenant_context(
    current_user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_org),
    project: Project | None = Depends(get_current_project),
) -> TenantContext:
    tenant_context.set_tenant(str(org.id), str(project.id) if project else None)
    return tenant_context


# API Key authentication
class APIKeyAuth:
    def __init__(self):
        self.scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/api-key")

    async def __call__(
        self,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
    ) -> tuple[User, Organization | None]:
        # Check if it's an API key (format: sk_...)
        if token.startswith("sk_"):
            from backend.database.models.api_key import APIKey, API_KEY_PREFIX_LENGTH
            # verify_password is the module-level import from passwords.py —
            # single source of truth (finding 2f29e692: hash-scheme drift).

            # Find API key by prefix. Length must match the stored prefix
            # (raw[:API_KEY_PREFIX_LENGTH] in api_keys.py) or keys are unfindable.
            prefix = token[:API_KEY_PREFIX_LENGTH]
            api_keys = await db.execute(select(APIKey).where(APIKey.key_prefix == prefix).where(APIKey.is_active))
            api_key = api_keys.scalar_one_or_none()

            if not api_key or not verify_password(token, api_key.key_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key",
                )

            # Check expiration
            if api_key.expires_at and api_key.expires_at < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key expired",
                )

            # Check scopes if needed
            # Update last used (persist — the session outlives this dependency).
            api_key.last_used_at = datetime.utcnow()
            await db.commit()

            user = await db.get(User, api_key.created_by)
            org = await db.get(Organization, api_key.organization_id)

            return user, org

        # Fall back to JWT
        payload = auth_manager.verify_token(token)
        user = await db.get(User, payload.sub)
        org = None
        if payload.org_id:
            org = await db.get(Organization, payload.org_id)
        return user, org


api_key_auth = APIKeyAuth()


# OAuth2/OIDC Integration
class OAuth2Provider:
    def __init__(self):
        self.providers: dict[str, OAuth2Config] = {}

    def register(self, name: str, config: OAuth2Config):
        self.providers[name] = config

    def get_config(self, name: str) -> OAuth2Config | None:
        return self.providers.get(name)

    async def get_user_info(self, provider: str, token: str) -> dict[str, Any]:
        config = self.get_config(provider)
        if not config:
            raise ValueError(f"Unknown provider: {provider}")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                config.userinfo_endpoint,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            return response.json()

    async def exchange_code(self, provider: str, code: str) -> TokenResponse:
        config = self.get_config(provider)
        if not config:
            raise ValueError(f"Unknown provider: {provider}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.token_endpoint,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": config.redirect_uri,
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                },
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return TokenResponse(**response.json())


class OAuth2Config:
    def __init__(
        self,
        name: str,
        authorization_endpoint: str,
        token_endpoint: str,
        userinfo_endpoint: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: list[str] = None,
    ):
        self.name = name
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.userinfo_endpoint = userinfo_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes or ["openid", "profile", "email"]


class TokenResponse:
    def __init__(self, access_token: str, refresh_token: str = "", expires_in: int = 3600, token_type: str = "Bearer"):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.token_type = token_type


# Global OAuth2 provider
oauth2_provider = OAuth2Provider()

# Register default providers
if config.auth.oidc_enabled:
    oauth2_provider.register(
        "oidc",
        OAuth2Config(
            name="oidc",
            authorization_endpoint=f"{config.auth.oidc_issuer_url}/authorize",
            token_endpoint=f"{config.auth.oidc_issuer_url}/token",
            userinfo_endpoint=f"{config.auth.oidc_issuer_url}/userinfo",
            client_id=config.auth.oidc_client_id,
            client_secret=config.auth.oidc_client_secret,
            redirect_uri=config.auth.oidc_redirect_uri,
            scopes=config.auth.oidc_scopes.split(","),
        ),
    )

if config.auth.github_oauth_enabled:
    oauth2_provider.register(
        "github",
        OAuth2Config(
            name="github",
            authorization_endpoint="https://github.com/login/oauth/authorize",
            token_endpoint="https://github.com/login/oauth/access_token",
            userinfo_endpoint="https://api.github.com/user",
            client_id=config.auth.github_client_id,
            client_secret=config.auth.github_client_secret,
            redirect_uri="http://localhost:8000/api/v1/auth/github/callback",
            scopes=["user:email", "read:org"],
        ),
    )

if config.auth.google_oauth_enabled:
    oauth2_provider.register(
        "google",
        OAuth2Config(
            name="google",
            authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
            token_endpoint="https://oauth2.googleapis.com/token",
            userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
            client_id=config.auth.google_client_id,
            client_secret=config.auth.google_client_secret,
            redirect_uri="http://localhost:8000/api/v1/auth/google/callback",
            scopes=["openid", "profile", "email"],
        ),
    )


# Role/Permission constants
class Permissions:
    # Organization
    ORG_CREATE = "organization:create"
    ORG_READ = "organization:read"
    ORG_UPDATE = "organization:update"
    ORG_DELETE = "organization:delete"
    ORG_MANAGE_MEMBERS = "organization:manage_members"
    ORG_MANAGE_BILLING = "organization:manage_billing"

    # Project
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_MANAGE_MEMBERS = "project:manage_members"

    # Workflow
    WORKFLOW_CREATE = "workflow:create"
    WORKFLOW_READ = "workflow:read"
    WORKFLOW_UPDATE = "workflow:update"
    WORKFLOW_DELETE = "workflow:delete"
    WORKFLOW_EXECUTE = "workflow:execute"
    WORKFLOW_MANAGE = "workflow:manage"

    # Agent
    AGENT_CREATE = "agent:create"
    AGENT_READ = "agent:read"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_EXECUTE = "agent:execute"

    # Knowledge Base
    KB_CREATE = "knowledge_base:create"
    KB_READ = "knowledge_base:read"
    KB_UPDATE = "knowledge_base:update"
    KB_DELETE = "knowledge_base:delete"
    KB_INGEST = "knowledge_base:ingest"
    KB_SEARCH = "knowledge_base:search"

    # Plugin
    PLUGIN_INSTALL = "plugin:install"
    PLUGIN_READ = "plugin:read"
    PLUGIN_UPDATE = "plugin:update"
    PLUGIN_DELETE = "plugin:delete"
    PLUGIN_EXECUTE = "plugin:execute"

    # Provider
    PROVIDER_CREATE = "provider:create"
    PROVIDER_READ = "provider:read"
    PROVIDER_UPDATE = "provider:update"
    PROVIDER_DELETE = "provider:delete"

    # User Management
    USER_INVITE = "user:invite"
    USER_REMOVE = "user:remove"
    USER_MANAGE_ROLES = "user:manage_roles"

    # Audit
    AUDIT_READ = "audit:read"

    # Admin
    ADMIN_ACCESS = "admin:access"
    SYSTEM_CONFIG = "system:config"


# Default role permissions
DEFAULT_ROLE_PERMISSIONS = {
    OrgUserRole.OWNER: [
        Permissions.ORG_CREATE,
        Permissions.ORG_READ,
        Permissions.ORG_UPDATE,
        Permissions.ORG_DELETE,
        Permissions.ORG_MANAGE_MEMBERS,
        Permissions.ORG_MANAGE_BILLING,
        Permissions.PROJECT_CREATE,
        Permissions.PROJECT_READ,
        Permissions.PROJECT_UPDATE,
        Permissions.PROJECT_DELETE,
        Permissions.PROJECT_MANAGE_MEMBERS,
        Permissions.WORKFLOW_CREATE,
        Permissions.WORKFLOW_READ,
        Permissions.WORKFLOW_UPDATE,
        Permissions.WORKFLOW_DELETE,
        Permissions.WORKFLOW_EXECUTE,
        Permissions.WORKFLOW_MANAGE,
        Permissions.AGENT_CREATE,
        Permissions.AGENT_READ,
        Permissions.AGENT_UPDATE,
        Permissions.AGENT_DELETE,
        Permissions.AGENT_EXECUTE,
        Permissions.KB_CREATE,
        Permissions.KB_READ,
        Permissions.KB_UPDATE,
        Permissions.KB_DELETE,
        Permissions.KB_INGEST,
        Permissions.KB_SEARCH,
        Permissions.PLUGIN_INSTALL,
        Permissions.PLUGIN_READ,
        Permissions.PLUGIN_UPDATE,
        Permissions.PLUGIN_DELETE,
        Permissions.PLUGIN_EXECUTE,
        Permissions.PROVIDER_CREATE,
        Permissions.PROVIDER_READ,
        Permissions.PROVIDER_UPDATE,
        Permissions.PROVIDER_DELETE,
        Permissions.USER_INVITE,
        Permissions.USER_REMOVE,
        Permissions.USER_MANAGE_ROLES,
        Permissions.AUDIT_READ,
        Permissions.ADMIN_ACCESS,
        Permissions.SYSTEM_CONFIG,
    ],
    OrgUserRole.ADMIN: [
        Permissions.ORG_READ,
        Permissions.ORG_UPDATE,
        Permissions.ORG_MANAGE_MEMBERS,
        Permissions.PROJECT_CREATE,
        Permissions.PROJECT_READ,
        Permissions.PROJECT_UPDATE,
        Permissions.PROJECT_DELETE,
        Permissions.PROJECT_MANAGE_MEMBERS,
        Permissions.WORKFLOW_CREATE,
        Permissions.WORKFLOW_READ,
        Permissions.WORKFLOW_UPDATE,
        Permissions.WORKFLOW_DELETE,
        Permissions.WORKFLOW_EXECUTE,
        Permissions.WORKFLOW_MANAGE,
        Permissions.AGENT_CREATE,
        Permissions.AGENT_READ,
        Permissions.AGENT_UPDATE,
        Permissions.AGENT_DELETE,
        Permissions.AGENT_EXECUTE,
        Permissions.KB_CREATE,
        Permissions.KB_READ,
        Permissions.KB_UPDATE,
        Permissions.KB_DELETE,
        Permissions.KB_INGEST,
        Permissions.KB_SEARCH,
        Permissions.PLUGIN_INSTALL,
        Permissions.PLUGIN_READ,
        Permissions.PLUGIN_UPDATE,
        Permissions.PLUGIN_DELETE,
        Permissions.PLUGIN_EXECUTE,
        Permissions.PROVIDER_CREATE,
        Permissions.PROVIDER_READ,
        Permissions.PROVIDER_UPDATE,
        Permissions.PROVIDER_DELETE,
        Permissions.USER_INVITE,
        Permissions.USER_REMOVE,
        Permissions.USER_MANAGE_ROLES,
        Permissions.AUDIT_READ,
    ],
    OrgUserRole.MEMBER: [
        Permissions.ORG_READ,
        Permissions.PROJECT_READ,
        Permissions.PROJECT_UPDATE,
        Permissions.WORKFLOW_READ,
        Permissions.WORKFLOW_EXECUTE,
        Permissions.AGENT_READ,
        Permissions.AGENT_EXECUTE,
        Permissions.KB_READ,
        Permissions.KB_SEARCH,
        Permissions.PLUGIN_READ,
        Permissions.PLUGIN_EXECUTE,
        Permissions.PROVIDER_READ,
    ],
    OrgUserRole.VIEWER: [
        Permissions.ORG_READ,
        Permissions.PROJECT_READ,
        Permissions.WORKFLOW_READ,
        Permissions.AGENT_READ,
        Permissions.KB_READ,
        Permissions.KB_SEARCH,
        Permissions.PLUGIN_READ,
        Permissions.PROVIDER_READ,
    ],
}


async def initialize_default_roles(db: AsyncSession, org_id: str):
    """Create default roles for a new organization."""
    for role_name, permissions in DEFAULT_ROLE_PERMISSIONS.items():
        # Check if role exists
        existing = await db.execute(
            select(Role).where(and_(Role.name == role_name.value, Role.organization_id == org_id))
        )
        if existing.scalar_one_or_none():
            continue

        role = Role(
            name=role_name.value,
            description=f"Default {role_name.value} role",
            is_system=True,
            organization_id=org_id,
        )
        db.add(role)
        await db.flush()

        # Assign permissions
        for perm_name in permissions:
            perm = await db.execute(select(Permission).where(Permission.name == perm_name))
            perm_obj = perm.scalar_one_or_none()
            if not perm_obj:
                # Create permission
                resource, action = perm_name.split(":")
                perm_obj = Permission(
                    name=perm_name,
                    resource=resource,
                    action=action,
                    is_system=True,
                )
                db.add(perm_obj)
                await db.flush()

            role.permissions.append(perm_obj)

    await db.commit()


async def assign_user_role(
    db: AsyncSession,
    user_id: str,
    role_name: str,
    org_id: str,
    project_id: str | None = None,
    expires_at: datetime | None = None,
) -> UserRole:
    """Assign a role to a user in an organization/project."""
    role = await db.execute(select(Role).where(and_(Role.name == role_name, Role.organization_id == org_id)))
    role = role.scalar_one_or_none()
    if not role:
        raise ValueError(f"Role {role_name} not found in organization {org_id}")

    # Check if already assigned
    existing = await db.execute(
        select(UserRole).where(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role.id,
                UserRole.organization_id == org_id,
                UserRole.project_id == project_id,
            )
        )
    )
    if existing.scalar_one_or_none():
        return existing.scalar_one()

    user_role = UserRole(
        user_id=user_id,
        role_id=role.id,
        organization_id=org_id,
        project_id=project_id,
        expires_at=expires_at,
    )
    db.add(user_role)
    await db.commit()
    await db.refresh(user_role)
    return user_role
