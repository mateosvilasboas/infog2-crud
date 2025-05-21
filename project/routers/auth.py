from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project.database import get_db
from project.models import User
from project.schemas import Token
from project.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
    responses={404: {'description': 'Not found'}},
)

Session = Annotated[AsyncSession, Depends(get_db)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2Form, session: Session):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Wrong email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Wrong email or password',
        )

    access_token = create_access_token(data={'sub': user.email})
    token_type = 'bearer'

    token = {'access_token': access_token, 'token_type': token_type}

    return token


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(current_user: CurrentUser):
    new_access_token = create_access_token(data={'sub': current_user.email})
    token_type = 'bearer'

    token = {'access_token': new_access_token, 'token_type': token_type}

    return token
