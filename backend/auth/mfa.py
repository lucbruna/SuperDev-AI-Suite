import pyotp
import qrcode
from io import BytesIO
import base64


class MFAHandler:
    ISSUER: str = "SuperDev"

    @staticmethod
    def generate_secret() -> str:
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(
        username: str,
        secret: str,
        issuer: str = ISSUER,
    ) -> str:
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)
        qr = qrcode.make(totp_uri)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"

    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
