import asyncio

from fastapi import FastAPI
import uvicorn

from db.database import init_models
from routes.authentication import authrouter
from routes.users import usersrouter


API_URL = "/api/v1"


app = FastAPI()

app.include_router(authrouter, prefix=f"{API_URL}/auth")
app.include_router(usersrouter, prefix=f"{API_URL}/users")


if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
