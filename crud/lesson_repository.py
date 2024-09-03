from typing import Optional

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.course_model import Lesson
from schemas.course_schema import LessonCreate


async def create_new_lesson(
    session: AsyncSession,
    lesson_data: LessonCreate
) -> Lesson:
    new_lesson = Lesson(**lesson_data.model_dump())
    session.add(new_lesson)
    await session.commit()
    return new_lesson


async def get_lesson_by_id(
    session: AsyncSession,
    id: int
) -> Optional[Lesson]:
    query = select(Lesson).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def get_paginated_lessons(
    session: AsyncSession,
    params: Params,
    course_id: int
):
    return await paginate(
        session,
        select(Lesson)
        .filter_by(course_id=course_id)
        .order_by(Lesson.title),
        params
    )
