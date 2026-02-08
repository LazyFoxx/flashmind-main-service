import base64
import json
from uuid import UUID

from authlib.jose import JoseError
from authlib.jose.errors import ExpiredTokenError, InvalidClaimError

from src.application.exceptions import InvalidTokenError
from src.core.settings.auth import AuthSettings

from .jwks_client import JWKSClient


class AuthService:
    def __init__(self, settings: AuthSettings, jwks: JWKSClient):
        self.settings = settings
        self.jwks = jwks

    async def decode_token(self, token: str) -> UUID:
        def b64url_decode(data: str) -> bytes:
            padding = "=" * (-len(data) % 4)
            return base64.urlsafe_b64decode(data + padding)

        try:
            header_b64, _, *_ = token.split(".")
            header = json.loads(b64url_decode(header_b64))

            kid = header["kid"]
            key = await self.jwks.get_key(kid)

            claims = self.settings.jwt.decode(
                token,
                key,
                claims_options={
                    "iss": {"essential": True, "value": self.settings.issuer},
                    "sub": {"essential": True},
                    "exp": {"essential": True},
                    "iat": {"essential": True},
                },
            )
            claims.validate()

            return UUID(claims["sub"])

        except (ExpiredTokenError, InvalidClaimError, JoseError, ValueError) as e:
            raise InvalidTokenError from e
