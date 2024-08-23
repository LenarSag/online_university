from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, ForeignKey, String, DECIMAL, Table
from sqlalchemy_utils import URLType
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship, validates
)

from models.base import Base


user_group = Table(
    "user_group",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "group_id",
        ForeignKey("group.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(250))
    title: Mapped[str] = mapped_column(String(250))
    start_date: Mapped[datetime] = mapped_column(nullable=False)
    price: Mapped[DECIMAL] = mapped_column(
        DECIMAL(precision=9, scale=2),
        nullable=False,
        default=Decimal(0.00)
    )

    users = relationship(
        "User",
        secondary="subscription",
        back_populates="courses"
    )
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan"
    )
    groups: Mapped[list["Group"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.title


class Lesson(Base):
    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("course.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(250))
    link = mapped_column(URLType, nullable=False)

    course: Mapped["Course"] = relationship(
        back_populates="lessons",
    )

    def __str__(self) -> str:
        return self.title


class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("course.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(100))

    course: Mapped["Course"] = relationship(
        back_populates="groups",
    )
    users = relationship(
        "User",
        secondary="user_group",
        back_populates="groups",
    )

    @validates("users")
    def validate_users_count(self, key, value):
        if len(self.users) > 30:
            raise ValueError("Group is full")
        return value

    def __str__(self) -> str:
        return self.title
