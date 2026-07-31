"""
Security Protocols
"""

from enum import Enum


class SecurityProtocol(Enum):
    TLS_1_3 = "tls_1_3"
    TLS_1_2 = "tls_1_2"
    MTLS = "mtls"


class AuthenticationMethod(Enum):
    PASSWORD = "password"
    MFA = "mfa"
    BIOMETRIC = "biometric"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    SSO = "sso"


class AuthorizationModel(Enum):
    RBAC = "rbac"
    ABAC = "abac"
    ACL = "acl"


class EncryptionStandard(Enum):
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    RSA_4096 = "rsa_4096"
    CHACHA20_POLY1305 = "chacha20_poly1305"


@dataclass
class SecurityProtocolConfig:
    protocol: SecurityProtocol = SecurityProtocol.TLS_1_3
    auth_method: AuthenticationMethod = AuthenticationMethod.MFA
    auth_model: AuthorizationModel = AuthorizationModel.RBAC
    encryption: EncryptionStandard = EncryptionStandard.AES_256_GCM

    def to_dict(self) -> dict[str, str]:
        return {
            "protocol": self.protocol.value,
            "auth_method": self.auth_method.value,
            "auth_model": self.auth_model.value,
            "encryption": self.encryption.value,
        }
