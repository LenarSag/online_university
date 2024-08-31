from typing import Optional
from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from crud.courses_repository import create_new_course, delete_course, get_course_by_id, get_paginated_courses, update_course
from db.database import get_session
from models.course_model import Course
from models.user_model import User
from permissions.rbac import check_role
from schemas.course_schema import CourseCreate, CourseData, CourseUpdate
from security.security import get_current_user


coursesrouter = APIRouter()


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


@coursesrouter.post(
    "/",
    response_model=CourseCreate,
    status_code=status.HTTP_201_CREATED
)
@check_role(["admin"])
async def create_course(
    course_data: CourseCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    new_course = await create_new_course(
        session, course_data
    )
    return new_course


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


@coursesrouter.patch("/{id}")
@check_role(["admin"])
async def update_course_data(
    id: int,
    new_course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    course_to_update = await get_course_or_404(session, id)
    updated_course = await update_course(
        session, course_to_update, new_course_data
    )
    return updated_course



@coursesrouter.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@check_role(["admin"])
async def delete_course_data(
    id: int,
    new_course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    course_to_delete = await get_course_or_404(session, id)
    await delete_course(session, course_to_delete)
