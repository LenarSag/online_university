
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.course_model import Course


async def get_course_by_id(
    session: AsyncSession,
    id: int
):
    query = (
        select(Course)
        .filter_by(id=id)
        .options(selectinload(Course.lessons), selectinload(Course.users))
    )
    result = await session.execute(query)
    return result.scalar()


async def get_paginated_courses(
    session: AsyncSession, params: Params
):
    return await paginate(
        session,
        select(Course)
        .options(selectinload(Course.lessons), selectinload(Course.users))
        .order_by(Course.title), params
    )
