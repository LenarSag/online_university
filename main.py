import asyncio

from fastapi import FastAPI
import uvicorn

from db.database import init_models


app = FastAPI()

if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
