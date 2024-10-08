from decimal import Decimal
import re
from typing import Optional
from typing_extensions import Annotated

from fastapi.exceptions import ValidationException
from pydantic import BaseModel, EmailStr, Field, field_validator

from models.user_model import UserRoles


class UserAuthentication(BaseModel):
    email: EmailStr = Field(max_length=50)
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        password_regex = re.compile(
            r"^"
            r"(?=.*[a-z])"
            r"(?=.*[A-Z])"
            r"(?=.*\d)"
            r"(?=.*[@$!%*?&])"
            r"[A-Za-z\d@$!%*?&]"
            r"{8,}$"
        )
        if not password_regex.match(value):
            raise ValidationException(
                "Password must be at least 8 characters long, include an "
                "uppercase letter, a lowercase letter, a number, "
                "and a special character."
            )
        return value


class UserCreate(UserAuthentication):
    username: str = Field(
        max_length=50, pattern=r"^[\w.@+-]+$"
    )
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)


class UserEdit(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: UserRoles = Field(default=UserRoles.USER)

    class Config:
        from_attributes = True
        use_enum_values = True


class UserBase(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool

    class Config:
        from_attributes = True


class BalanceBase(BaseModel):
    amount: Annotated[Decimal, Field(ge=0.0)]


class UserWithBalance(UserBase):
    balance: BalanceBase
