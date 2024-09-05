from decimal import Decimal
from typing import Optional

from pydantic import EmailStr
from sqlalchemy.future import select
from sqlalchemy.sql.expression import or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.course_model import Course, Group
from models.user_model import Balance, User
from schemas.user_schema import UserCreate, UserEdit


async def check_username_and_email(
    session: AsyncSession, username: str, email: EmailStr
) -> Optional[User]:
    query = select(User).where(or_(
        User.username == username, User.email == email
    ))
    result = await session.execute(query)
    return result.scalar()


async def check_username_and_email_for_update(
    session: AsyncSession,
    username: Optional[str],
    email: Optional[str],
    id: int
) -> Optional[User]:
    query = select(User).where(
        and_(
            or_(
                User.username == username,
                User.email == email
            ),
            User.id != id
        )
    )
    result = await session.execute(query)
    return result.scalar()


async def get_user_by_id(
    session: AsyncSession, user_id: int
) -> Optional[User]:
    query = select(User).filter_by(id=user_id)
    result = await session.execute(query)
    return result.scalar()


async def get_user_by_email(
    session: AsyncSession,
    email: EmailStr
) -> Optional[User]:
    query = select(User).filter_by(email=email)
    result = await session.execute(query)
    return result.scalar()


async def get_user_balance(
    session: AsyncSession,
    user: User
) -> User:
    await session.refresh(user, attribute_names=("balance",))
    return user


async def get_user_with_balance_and_courses(
    session: AsyncSession,
    user: User
) -> User:
    await session.refresh(user, attribute_names=("balance", "courses"))
    return user


async def update_balance(
    session: AsyncSession,
    user: User,
    new_amount: Decimal
) -> User:
    await session.refresh(user, attribute_names=("balance",))
    user.balance.amount = new_amount
    await session.commit()
    await session.refresh(user, attribute_names=("balance",))
    return user


async def create_user(
    session: AsyncSession,
    user_data: UserCreate
) -> User:
    user = User(**user_data.model_dump())
    session.add(user)
    await session.flush()

    balance = Balance(user_id=user.id)
    session.add(balance)
    await session.commit()

    return user


async def update_user(
    session: AsyncSession,
    user: User,
    new_user_data: UserEdit
) -> User:
    update_data = new_user_data.model_dump()
    for key, value in update_data.items():
        if value:
            setattr(user, key, value)

    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(
    session: AsyncSession,
    user: User
) -> None:
    await session.delete(user)
    await session.commit()


async def buy_new_course(
    session: AsyncSession,
    course: Course,
    user: User,
    group: Group
) -> None:
    user.courses.append(course)
    user.balance.amount -= course.price
    await session.refresh(group, attribute_names=("users",))
    group.users.append(user)
    await session.flush()
    await session.commit()
