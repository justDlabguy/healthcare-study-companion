from typing import Annotated, Optional, TypeVar, Any, Callable

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .db import get_db

# For dependency injection
T = TypeVar("T")

get_bearer_token = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    db: Annotated[Session, Depends(get_db)], 
    token: Annotated[str, Depends(oauth2_scheme)]
) -> models.User:
    """
    Dependency to get the current user from the JWT token.
    
    Args:
        db: Database session
        token: JWT token from Authorization header
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=["HS256"]
        )
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
    except (JWTError, ValidationError) as e:
        raise credentials_exception from e

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


# Type alias for dependency injection
CurrentUser = Annotated[models.User, Depends(get_current_user)]


def require_role(required_role: str) -> Callable[[models.User], models.User]:
    """
    Dependency factory to enforce role-based access control.
    
    Args:
        required_role: Minimum role required to access the endpoint
        
    Returns:
        Callable that checks if the user has the required role
    """
    def role_checker(current_user: CurrentUser) -> models.User:
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role or admin",
            )
        return current_user

    return role_checker


# Common role-based dependencies
RequireAdmin = require_role("admin")
RequireTeacher = require_role("teacher")
RequireStudent = require_role("student")
