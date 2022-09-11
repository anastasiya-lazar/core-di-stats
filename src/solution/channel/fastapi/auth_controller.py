from typing import Optional

from bst_core.auth.authtokenvalidator import AuthTokenValidator
from bst_core.auth.client import Client
from config import AUTHENTICATOR_URL
from connexion.exceptions import OAuthProblem
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN


class AuthTokenApiKey(SecurityBase):
    def __init__(
        self,
        *,
        name: str,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True
    ):
        self.model: APIKey = APIKey(
            **{"in": APIKeyIn.header}, name="token", description=description
        )
        self.name = name
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    def __call__(self, request: Request) -> Optional[str]:
        api_key: str = request.headers.get(self.name, None)
        token: str = request.headers.get(self.model.name, "")
        if "Bearer" in token:
            token.replace("Bearer", "").strip()
        try:
            result = AuthTokenValidator(AUTHENTICATOR_URL).auth(
                token=token, api_key=api_key, provider=Client().verify_client(token)[1]
            )
            if not result:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN)
        except OAuthProblem as e:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(e))
