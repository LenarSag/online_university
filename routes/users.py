from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user_repository import (
    check_username_and_email_for_update,
    delete_user,
    get_user_balance, get_user_by_id,
    update_balance,
    update_user
)
from db.database import get_session
from models.user_model import User
from permissions.rbac import check_role
from schemas.user_schema import BalanceBase, UserBase, UserEdit, UserWithBalance
from security.security import get_current_user


usersrouter = APIRouter()


async def get_user_or_404(session: AsyncSession, id: int) -> Optional[User]:
    user = await get_user_by_id(session, id)
    if not user:
        raise HTTPException(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return user


@usersrouter.get("/me", response_model=UserWithBalance)
async def get_myself(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    user_with_balance = await get_user_balance(session, current_user)
    return user_with_balance


@usersrouter.get("/{id}", response_model=UserBase)
@check_role(["admin"])
async def get_user(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    user = await get_user_or_404(session, id)

    return user


@usersrouter.patch("/{id}", response_model=UserEdit)
@check_role(["admin"])
async def update_user_data(
    id: int,
    new_user_data: UserEdit,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    user_to_edit = await get_user_or_404(session, id)

    if new_user_data.username or new_user_data.email:
        existing_user = await check_username_and_email_for_update(
            session,
            new_user_data.username,
            new_user_data.email,
            id
        )
        if existing_user:
            if existing_user.username == new_user_data.username:
                raise HTTPException(
                    detail="Username already taken",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            raise HTTPException(
                detail="Email already registered",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    updated_user = await update_user(session, user_to_edit, new_user_data)
    return updated_user


@usersrouter.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@check_role(["admin"])
async def delete_user_data(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    user_to_delete = await get_user_or_404(session, id)
    await delete_user(session, user_to_delete)


@usersrouter.post("/{id}/balance", response_model=UserWithBalance)
@check_role(["admin"])
async def update_user_balance(
    id: int,
    balance: BalanceBase,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    user = await get_user_or_404(session, id)
    updated_user = await update_balance(session, user, balance.amount)

    return updated_user
