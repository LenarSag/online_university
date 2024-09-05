from typing import Optional
from fastapi_pagination import Page, Params
from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.courses_repository import get_course_by_id
from crud.lesson_repository import create_new_lesson, delete_lesson_data, get_lesson_by_id, get_paginated_lessons, update_lesson_data
from db.database import get_session
from models.course_model import Course, Lesson
from models.user_model import User
from permissions.rbac import check_admin_or_subscription, check_role
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
    session: Annotated[AsyncSession, Depends(get_session)],
    course_id: int = Path(..., title="The id of course"),
):
    course = await get_course_or_404(session, course_id)
    new_lesson = await create_new_lesson(
        session, lesson_data, course.id
    )
    return new_lesson


@lessonsrouter.get(
    "/{id}", response_model=LessonData
)
@check_admin_or_subscription
async def get_lesson(
    id: int,
    course_id: Annotated[int, Path(..., title="The id of course")],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    
):
    lesson = await get_lesson_or_404(session, id)
    return (
        LessonData(
            id=lesson.id,
            title=lesson.title,
            link=lesson.link,
            course_id=lesson.course_id,
        )
    )


@lessonsrouter.get(
    "/", response_model=Page[LessonData]
)
@check_admin_or_subscription
async def get_lessons(
    params: Params,
    course_id: Annotated[int, Path(..., title="The id of course")],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    course = await get_course_or_404(session, course_id)
    result = await get_paginated_lessons(session, params, course.id)
    result.items = [
        LessonData(
            id=lesson.id,
            title=lesson.title,
            link=lesson.link,
            course_id=lesson.course_id
        )
        for lesson in result.items
    ]

    return result


@lessonsrouter.patch("/{id}")
@check_role(["admin"])
async def update_lesson(
    id: int,
    new_lesson_data: LessonCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    lesson_to_update = await get_lesson_or_404(session, id)
    updated_lesson = await update_lesson_data(
        session, lesson_to_update, new_lesson_data
    )
    return updated_lesson


@lessonsrouter.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT
)
@check_role(["admin"])
async def delete_lesson(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    lesson_to_delete = await get_lesson_or_404(session, id)
    await delete_lesson_data(session, lesson_to_delete)
