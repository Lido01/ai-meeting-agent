from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.services.auth_service import verify_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    """
    Get the logged-in user's ID from JWT.
    """

    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return user_id