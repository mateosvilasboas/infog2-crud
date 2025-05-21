from http import HTTPStatus

import pytest
from sqlalchemy import select

from project.models import User
from project.schemas import UserPublic


def test_create_user(client):
    password = 'senha'
    response = client.post(
        '/users/',
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'password': password,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'name': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_create_user_with_existing_email(client):
    client.post(
        '/users/',
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'password': 'password123',
        },
    )

    response = client.post(
        '/users/',
        json={
            'name': 'alice two',
            'email': 'alice@example.com',
            'password': 'password456',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_get_users(client):
    response = client.get(
        '/users/',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_get_users_with_users(client, user):
    users_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [users_schema]}


def test_update_user_without_password(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'bob',
            'email': 'bob@email.com',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'name': 'bob',
        'email': 'bob@email.com',
        'id': 1,
    }


def test_update_user_with_password(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'bob',
            'email': 'bob@email.com',
            'password': 'senhanova',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'name': 'bob',
        'email': 'bob@email.com',
        'id': 1,
    }


def test_update_user_integrity_error(client, user, token):
    client.post(
        '/users',
        json={
            'name': 'bob',
            'email': 'bob@email.com',
            'password': 'senhaatual',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'bob2',
            'email': 'bob@email.com',
            'password': 'senhaatual',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_update_user_with_wrong_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'bruno',
            'email': 'bruno@teste.com',
            'password': 'novasenha',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


@pytest.mark.asyncio
async def test_delete_user(client, user, token, session):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}

    deleted_user = await session.scalar(select(User).where(User.id == user.id))  # noqa

    assert deleted_user.is_deleted is True
    assert deleted_user.deleted_at is not None


@pytest.mark.asyncio
async def test_delete_user_with_wrong_user(client, other_user, token, session):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}

    forbidden_user = await session.scalar(
        select(User).where(User.id == other_user.id)
    )  # noqa

    assert forbidden_user.is_deleted is False
    assert forbidden_user.deleted_at is None
