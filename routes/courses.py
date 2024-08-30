from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from crud.courses_repository import get_course_by_id, get_paginated_courses
from db.database import get_session
from models.user_model import User
from schemas.course_schema import CourseData
from security.security import get_current_user


coursesrouter = APIRouter()

@coursesrouter.get("/{id}", response_model=CourseData)
async def get_course(
    id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    course = await get_course_by_id(
        session, id
    )
    if course:
        return (
            CourseData(
                id=course.id,
                author=course.author,
                title=course.title,
                start_date=course.start_date,
                price=course.price,
                lessons_count=len(course.lessons),
                lessons=course.lessons,
                students_count=len(course.users)
                )
        )
    raise HTTPException(
        detail="Course not found",
        status_code=status.HTTP_404_NOT_FOUND
    )


@coursesrouter.get("/", response_model=Page[CourseData])
async def get_courses(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    params: Params = Depends()
):
    result = await get_paginated_courses(session, params)
    result.items = [
        CourseData(
            id=course.id,
            author=course.author,
            title=course.title,
            start_date=course.start_date,
            price=course.price,
            lessons_count=len(course.lessons),
            lessons=course.lessons,
            students_count=len(course.users)
        )
        for course in result.items
    ]

    return result
