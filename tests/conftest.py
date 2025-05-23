# ruff: noqa: E402
from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer
from validate_docbr import CPF

from project.database import get_db
from project.main import app
from project.models.base import Admin, Base, Client, Role
from project.security import get_password_hash


@pytest.fixture
def client(session):
    def get_db_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_db] = get_db_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def admin(session):
    cpf = CPF().generate()
    password = 'senha1'
    hashed_password = get_password_hash(password)
    role = Role.ADMIN
    user = AdminFactory(cpf=cpf, password=hashed_password, role=role)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def user(session):
    cpf = CPF().generate()
    password = 'senha1'
    hashed_password = get_password_hash(password)
    role = Role.CLIENT
    user = UserFactory(cpf=cpf, password=hashed_password, role=role)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def other_user(session):
    cpf = CPF().generate()
    password = 'senha2'
    hashed_password = get_password_hash(password)
    role = Role.CLIENT
    user = UserFactory(cpf=cpf, password=hashed_password, role=role)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def admin_token(client, admin):
    response = client.post(
        '/auth/token',
        data={'username': admin.email, 'password': admin.clean_password},
    )

    return response.json()['access_token']


class UserFactory(factory.Factory):
    class Meta:
        model = Client

    name = factory.Sequence(lambda n: f'client{n}')
    cpf = factory.Faker('cpf')
    email = factory.LazyAttribute(lambda obj: f'{obj.name}@teste.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.name}@example.com')
    role = factory.Faker('role')


class AdminFactory(factory.Factory):
    class Meta:
        model = Admin

    name = factory.Sequence(lambda n: f'admin{n}')
    cpf = factory.Faker('cpf')
    email = factory.LazyAttribute(lambda obj: f'{obj.name}@teste.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.name}@example.com')
    role = factory.Faker('role')
