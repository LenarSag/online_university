
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user_repository import check_username_and_email, create_user
from db.database import get_session
from schemas.user_schema import UserAuthentication, UserBase, UserCreate
from security.security import authenticate_user, create_access_token
from security.pwd_crypt import get_hashed_password


authrouter = APIRouter()

@authrouter.post("/users")
async def create_new_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    user = await check_username_and_email(
        session, user_data.username, user_data.email
    )
    if user:
        if user.username == user_data.username:
            raise HTTPException(
                detail="Username already taken",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        raise HTTPException(
            detail="Email already registered",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    user_data.password = get_hashed_password(user_data.password)
    new_user = await create_user(session, user_data)
    new_user_data = UserBase.model_validate(new_user)

    return Response(
        content=new_user_data.model_dump_json(),
        status_code=status.HTTP_201_CREATED
    )


@authrouter.post("/token/login")
async def get_token(
    user_data: UserAuthentication,
    session: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(
        session,
        user_data.email,
        user_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user)
    return {"access_token": access_token, "token_type": "Bearer"}
