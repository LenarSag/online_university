from typing import Optional
from fastapi_pagination import Page, Params
from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.courses_repository import get_course_by_id
from crud.lesson_repository import create_new_lesson, get_lesson_by_id, get_paginated_lessons
from db.database import get_session
from models.course_model import Course, Lesson
from models.user_model import User
from permissions.rbac import check_role
from schemas.course_schema import LessonCreate, LessonData
from security.security import get_current_user


lessonsrouter = APIRouter()


async def get_lesson_or_404(
    session: AsyncSession, id: int
) -> Optional[Lesson]:
    lesson = await get_lesson_by_id(session, id)
    if not lesson:
        raise HTTPException(
            detail="Lesson not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return lesson


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


@lessonsrouter.post(
    "/",
    response_model=LessonData,
    status_code=status.HTTP_201_CREATED
)
@check_role(["admin"])
async def create_lesson(
    lesson_data: LessonCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession
):
    new_lesson = await create_new_lesson(
        session, lesson_data
    )
    return new_lesson


@lessonsrouter.get(
    "/", response_model=Page[LessonData]
)
async def get_lessons(
    session: AsyncSession,
    params: Params,
    course_id: int = Path(..., title="The id of course")
):
    result = await get_paginated_lessons(session, params, course_id)
    result.items = [
        LessonData(
            id=lesson.id,
            title=lesson.title,
            link=lesson.link,
            course=lesson.course_id
        )
        for lesson in result.items
    ]

    return result

@lessonsrouter.get(
    "/{lesson_id}", response_model=LessonData
)
async def get_lesson(
    id: int,
    course_id: int = Path(..., title="The id of course"),
    session: AsyncSession = Depends(get_session)
):
    course = await get_course_or_404(session, course_id)
    lesson = await get_lesson_or_404(session, id)
    return lesson