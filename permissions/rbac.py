from functools import wraps

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from models.user_model import User
from security.security import get_current_user


def check_role(required_roles: list[str]):
    def decorator(func):
        """Checks if current user has required rights."""
        @wraps(func)
        async def wrapper(
            *args,
            current_user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_session),
            **kwargs
        ):
            if current_user.role.value not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            return await func(
                *args, current_user=current_user, session=session, **kwargs
            )
        return wrapper

    return decorator
