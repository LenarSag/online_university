
from typing import Optional
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.course_model import Course
from schemas.course_schema import CourseCreate, CourseUpdate


async def create_new_course(
    session: AsyncSession,
    course_data: CourseCreate
) -> Course:
    new_course = Course(**course_data.model_dump())
    session.add(new_course)
    await session.commit()
    return new_course


async def get_course_by_id(
    session: AsyncSession,
    id: int
) -> Optional[Course]:
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
        .order_by(Course.title),
        params
    )


async def update_course_data(
    session: AsyncSession,
    course: Course,
    new_course_data: CourseUpdate
) -> Course:
    update_data = new_course_data.model_dump()
    for key, value in update_data.items():
        if value:
            setattr(course, key, value)
    await session.commit()
    await session.refresh(course)
    return course


async def delete_course_data(
    session: AsyncSession,
    course: Course
) -> None:
    await session.delete(course)
    await session.commit()
