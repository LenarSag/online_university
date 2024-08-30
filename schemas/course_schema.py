from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, HttpUrl


class LessonMini(BaseModel):
    title: str

    class Config:
        from_attributes = True


class LessonCreate(LessonMini):
    link: HttpUrl
    course: int

    class Config:
        from_attributes = True


class LessonData(LessonCreate):
    id: int


class CourseCreate(BaseModel):
    author: str
    title: str
    start_date: datetime
    price: Decimal

    class Config:
        from_attributes = True


class CourseData(CourseCreate):
    id: int
    lessons_count: int
    lessons: list[LessonMini]
    students_count: int
