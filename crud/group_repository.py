from typing import Optional

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.course_model import Group
from models.user_model import User
from schemas.course_schema import GroupCreate


async def create_new_group(
    session: AsyncSession,
    group_data: GroupCreate,
    course_id: int
) -> Group:
    new_group = Group(
        **group_data.model_dump(),
        course_id=course_id
    )
    session.add(new_group)
    await session.commit()
    return new_group


async def get_group_by_id(
    session: AsyncSession,
    id: int
) -> Optional[Group]:
    query = (
        select(Group)
        .filter_by(id=id)
        .options(selectinload(Group.users))
    )
    result = await session.execute(query)
    return result.scalar()


async def get_paginated_groups(
    session: AsyncSession,
    params: Params,
    course_id: int
):
    return await paginate(
        session,
        select(Group)
        .filter_by(course_id=course_id)
        .options(selectinload(Group.users))
        .order_by(Group.title),
        params
    )


async def get_available_group_for_course(
    session: AsyncSession,
    course_id: int
):
    stmt = (
        select(Group)
        .filter_by(course_id=course_id)
        .outerjoin(Group.users)
        .group_by(Group.id)
        .having(func.count(User.id) < 30)
        .order_by(func.count(User.id))
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def update_group_data(
    session: AsyncSession,
    group: Group,
    new_group_data: GroupCreate
) -> Group:
    group.title = new_group_data.title
    await session.commit()
    await session.refresh(group)
    return group


async def delete_group_data(
    session: AsyncSession,
    group: Group
) -> None:
    await session.delete(group)
    await session.commit()
