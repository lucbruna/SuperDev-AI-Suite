from datetime import timedelta

from jose import JWTError, jwt
from pydantic import SecretStr

from backend.utils.datetime import utc_now


class JWTManager:
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440

    def __init__(
        self,
        secret_key: str,
        algorithm: str = ALGORITHM,
        access_token_expire: int = ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire: int = REFRESH_TOKEN_EXPIRE_MINUTES,
    ) -> None:
        if not secret_key or secret_key == "super-dev-secret-key-change-in-production":
            raise ValueError(
                "JWT secret_key must be configured via JWT_SECRET_KEY environment variable"
            )
        self.secret_key = SecretStr(secret_key)
        self.algorithm = algorithm
        self.access_token_expire = access_token_expire
        self.refresh_token_expire = refresh_token_expire

    def create_access_token(
        self,
        subject: str,
        expires_delta: timedelta | None = None,
    ) -> str:
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire)
        if expires_delta.total_seconds() <= 0:
            return ""
        now = utc_now()
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + expires_delta,
            "type": "access",
        }
        return jwt.encode(payload, self.secret_key.get_secret_value(), algorithm=self.algorithm)

    def create_refresh_token(
        self,
        subject: str,
        expires_delta: timedelta | None = None,
    ) -> str:
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.refresh_token_expire)
        now = utc_now()
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + expires_delta,
            "type": "refresh",
        }
        return jwt.encode(payload, self.secret_key.get_secret_value(), algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token,
                self.secret_key.get_secret_value(),
                algorithms=[self.algorithm],
            )
            return payload
        except JWTError:
            return None
