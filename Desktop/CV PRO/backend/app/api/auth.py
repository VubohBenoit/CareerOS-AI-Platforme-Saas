"""Auth Endpoints - Signup, Login, Refresh"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import (
    UserCreate,
    UserLogin,
    AuthResponse,
    RefreshTokenRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register new user account.

    Returns user data and JWT tokens.

    **Errors:**
    - 400: Email already exists or validation failed
    - 422: Unprocessable entity (invalid data)
    """
    try:
        result = AuthService.signup(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed",
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return tokens.

    **Errors:**
    - 401: Invalid credentials
    - 400: User account disabled
    """
    try:
        result = AuthService.login(
            db=db,
            email=credentials.email,
            password=credentials.password,
        )
        return result

    except ValueError as e:
        error_msg = str(e)
        status_code = (
            status.HTTP_401_UNAUTHORIZED
            if "Invalid email or password" in error_msg
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=error_msg)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/refresh", response_model=dict)
async def refresh(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Get new access token using refresh token.

    **Errors:**
    - 401: Invalid refresh token
    """
    try:
        result = AuthService.refresh(
            db=db,
            refresh_token=request.refresh_token,
        )
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side mainly).

    Note: JWT tokens are stateless, so logout is just client-side.
    Client should delete tokens from localStorage.
    """
    return {"message": "Logged out successfully"}
