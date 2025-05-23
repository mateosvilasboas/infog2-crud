# ruff: noqa: E402, F401, I001

from . import models
from fastapi import FastAPI
from .routers.auth import router as auth_router
from .routers.users import admin_router, client_router

app = FastAPI()

app.include_router(admin_router)
app.include_router(client_router)
app.include_router(auth_router)


@app.get('/')
async def root():
    return {'message': 'Hello World'}
