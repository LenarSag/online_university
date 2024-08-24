
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user_repository import check_username_and_email, create_user, get_user_by_id
from db.database import get_session
from models.user_model import User
from permissions.rbac import check_role
from schemas.user_schema import UserBase
from security.security import  get_current_user


usersrouter = APIRouter()


@usersrouter.get("/me", response_model=UserBase)
async def get_myself(
    current_user: UserBase = Depends(get_current_user),
):
    return current_user


@usersrouter.get("/{id}", response_model=UserBase)
@check_role(["admin"])
async def get_user(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    user = await get_user_by_id(session, id)
    if not user:
        raise HTTPException(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return user
