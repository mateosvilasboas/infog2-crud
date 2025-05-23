from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.base import Admin, Client, Role, User
from ..schemas.others import Message
from ..schemas.users import (
    AdminSchemaCreate,
    UserFilterPage,
    UserList,
    UserPublic,
    UserSchemaCreate,
    UserSchemaUpdate,
)
from ..security import get_current_user, get_password_hash

Session = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

client_router = APIRouter(
    prefix='/client',
    tags=['clients'],
    responses={404: {'description': 'Not found'}},
)
admin_router = APIRouter(
    prefix='/admin',
    tags=['admins'],
    responses={404: {'description': 'Not found'}},
)


@admin_router.post(
    '/', response_model=UserPublic, status_code=HTTPStatus.CREATED
)
async def create_user(
    user: AdminSchemaCreate,
    session: Session,
    current_user: CurrentUser,
):
    if not isinstance(current_user, Admin):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Not enough permissions',
        )

    if user.role not in Role._value2member_map_:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Role does not exist',
        )

    db_user = await session.scalar(
        select(User).where(or_(User.email == user.email, User.cpf == user.cpf))
    )

    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )
        if db_user.cpf == user.cpf:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='CPF already exists'
            )

    hashed_password = get_password_hash(user.password)

    if user.role == Role.ADMIN.value:
        db_user = Admin(
            name=user.name,
            email=user.email,
            cpf=user.cpf,
            password=hashed_password,
        )
    elif user.role == Role.CLIENT.value:
        db_user = Client(
            name=user.name,
            email=user.email,
            cpf=user.cpf,
            password=hashed_password,
        )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@admin_router.get('/', response_model=UserList)
async def get_users(
    filter_users: Annotated[UserFilterPage, Query()],
    session: Session,
    current_user: CurrentUser,
):
    if not isinstance(current_user, Admin):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Not enough permissions',
        )

    query = select(User).where(User.is_deleted == False)  # noqa

    if filter_users.email:
        query = query.filter(User.email == filter_users.email)

    if filter_users.name:
        query = query.filter(User.name == filter_users.name)

    query = query.offset(filter_users.offset).limit(filter_users.limit)

    result = await session.scalars(query)
    users = result.all()

    return {'users': users}


@admin_router.delete('/{user_id}', response_model=Message)
async def delete_user(
    user_id: int,
    role: str,
    session: Session,
    current_user: CurrentUser,
):
    if not isinstance(current_user, Admin):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Not enough permissions',
        )

    if role not in Role._value2member_map_:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Invalid role specified'
        )

    role_enum = Role(role)
    user = await session.scalar(
        select(User).where(and_(User.id == user_id, User.role == role_enum))
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    if user.is_deleted:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='User already deleted'
        )

    user.soft_delete()
    await session.commit()

    return {'message': 'User deleted'}


@client_router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=UserPublic
)
async def create_client(user: UserSchemaCreate, session: Session):
    db_user = await session.scalar(
        select(User).where(or_(User.email == user.email, User.cpf == user.cpf))
    )

    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )
        if db_user.cpf == user.cpf:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='CPF already exists'
            )

    hashed_password = get_password_hash(user.password)

    db_user = Client(
        name=user.name,
        email=user.email,
        cpf=user.cpf,
        password=hashed_password,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@client_router.put('/{user_id}', response_model=UserPublic)
async def update_client(
    user_id: int,
    user: UserSchemaUpdate,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    try:
        current_user.name = user.name
        current_user.email = user.email

        if user.password:
            current_user.password = get_password_hash(user.password)

        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email already exists',
        )


@client_router.delete('/{user_id}', response_model=Message)
async def delete_client(
    user_id: int, session: Session, current_user: CurrentUser
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    if current_user.is_deleted:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='User already deleted'
        )

    current_user.soft_delete()
    await session.commit()

    return {'message': 'User deleted'}
