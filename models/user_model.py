from decimal import Decimal
from enum import Enum as PyEnum
import re

from sqlalchemy import Column, Enum, ForeignKey, String, DECIMAL, Table
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship, validates
)

from models.base import Base


class UserRoles(PyEnum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRoles] = mapped_column(
        Enum(UserRoles, values_callable=lambda obj: [e.value for e in obj]),
        default=UserRoles.USER.value,
        server_default=UserRoles.USER.value,
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    balance: Mapped["Balance"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    courses = relationship(
        "Course",
        secondary="subscription",
        back_populates="users",
        )
    groups = relationship(
        "Group",
        secondary="user_group",
        back_populates="users",
        )

    @validates("username")
    def validate_username(self, key, value):
        username_regex = r"^[\w.@+-]+$"
        if not re.match(username_regex, value):
            raise ValueError("Username is invalid")
        return value

    @validates("email")
    def validate_email(self, key, value):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, value):
            raise ValueError("Invalid email format")
        return value

    def __str__(self) -> str:
        return self.username


class Balance(Base):
    __tablename__ = "balance"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    amount: Mapped[DECIMAL] = mapped_column(
        DECIMAL(precision=9, scale=2),
        nullable=False,
        default=Decimal(1000.00)
    )

    user: Mapped["User"] = relationship(back_populates="balance")

    @validates("amount")
    def validate_amount(self, key, value):
        if value < 0:
            raise ValueError("Balance can't be negative.")
        return value

    def __str__(self) -> str:
        return str(self.amount)


subscription = Table(
    "subscription",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "course_id",
        ForeignKey("course.id", ondelete="CASCADE"),
        primary_key=True
    )
)
