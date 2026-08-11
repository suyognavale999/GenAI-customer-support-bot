from fastapi import APIRouter

from app.api.dependencies import (
    CurrentUserDependency,
    DatabaseDependency,
)
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    database: DatabaseDependency,
) -> TokenResponse:
    access_token = AuthService(database).login(
        identity=request.username,
        password=request.password,
    )

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=CurrentUserResponse)
def get_current_user_profile(
    current_user: CurrentUserDependency,
) -> CurrentUserResponse:
    return CurrentUserResponse.model_validate(current_user)