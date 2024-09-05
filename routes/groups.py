from typing import Optional
from fastapi_pagination import Page, Params
from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.courses_repository import get_course_by_id
from crud.group_repository import create_new_group, get_group_by_id, get_paginated_groups
from db.database import get_session
from models.course_model import Course, Group
from models.user_model import User
from permissions.rbac import check_role
from schemas.course_schema import GroupBase, GroupCreate, GroupData
from security.security import get_current_user


groupsrouter = APIRouter()


async def get_group_or_404(
    session: AsyncSession, id: int
) -> Optional[Group]:
    group = await get_group_by_id(session, id)
    if not group:
        raise HTTPException(
            detail="Group not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return group


async def get_course_or_404(
    session: AsyncSession, id: int
) -> Optional[Course]:
    course = await get_course_by_id(session, id)
    if not course:
        raise HTTPException(
            detail="Course not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return course


@groupsrouter.post(
    "/",
    response_model=GroupBase,
    status_code=status.HTTP_201_CREATED
)
@check_role(["admin"])
async def create_group(
    group_data: GroupCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    course_id: int = Path(..., title="The id of course"),
):
    course = await get_course_or_404(session, course_id)
    group = await create_new_group(
        session, group_data, course.id
    )
    return group


@groupsrouter.get(
    "/{id}", response_model=GroupData
)
@check_role(["admin"])
async def get_group(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    group = await get_group_or_404(session, id)
    return (
        GroupData(
            id=group.id,
            title=group.title,
            course_id=group.course_id,
            users=group.users
        )
    )


@groupsrouter.get(
    "/", response_model=Page[GroupData]
)
@check_role(["admin"])
async def get_groups(
    params: Params,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    course_id: int = Path(..., title="The id of course")
):
    course = await get_course_or_404(session, course_id)
    result = await get_paginated_groups(session, params, course.id)
    result.items = [
        GroupData(
            id=group.id,
            course_id=group.course_id,
            title=group.title,
            users=group.users
        )
        for group in result.items
    ]

    return result
