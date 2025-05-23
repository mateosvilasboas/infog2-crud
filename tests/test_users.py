from http import HTTPStatus

import pytest
from sqlalchemy import select
from validate_docbr import CPF

from project.models.base import Role, User


def test_get_users(client, admin_token):
    response = client.get(
        '/admin/', headers={'Authorization': f'Bearer {admin_token}'}
    )

    users = response.json()['users']

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': users}


def test_create_client(client):
    password = 'senha'
    cpf = CPF().generate()
    response = client.post(
        '/client/',
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'cpf': cpf,
            'password': password,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'name': 'alice',
        'email': 'alice@example.com',
        'cpf': cpf,
        'id': 1,
        'role': Role.CLIENT.value,
    }


def test_create_client_invalid_cpf(client):
    password = 'senha'
    response = client.post(
        '/client/',
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'cpf': '00000000000',
            'password': password,
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Invalid CPF'}


def test_create_client_with_existing_email(client):
    cpf = CPF().generate()
    client.post(
        '/client/',
        json={
            'name': 'john',
            'email': 'alice@example.com',
            'cpf': cpf,
            'password': 'password123',
        },
    )
    cpf = CPF().generate()
    response = client.post(
        '/client/',
        json={
            'name': 'alice two',
            'email': 'alice@example.com',
            'cpf': cpf,
            'password': 'password456',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_create_client_with_existing_cpf(client):
    cpf = CPF().generate()
    client.post(
        '/client/',
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'cpf': cpf,
            'password': 'password123',
        },
    )

    response = client.post(
        '/client/',
        json={
            'name': 'alice two',
            'email': 'alice_2@example.com',
            'cpf': cpf,
            'password': 'password456',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'CPF already exists'}


def test_update_client_without_password(client, user, token):
    response = client.put(
        f'/client/{user.id}',
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
        'cpf': user.cpf,
        'id': 1,
        'role': Role.CLIENT.value,
    }


def test_update_client_with_password(client, user, token):
    response = client.put(
        f'/client/{user.id}',
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
        'cpf': user.cpf,
        'email': 'bob@email.com',
        'id': 1,
        'role': Role.CLIENT.value,
    }


def test_update_user_integrity_error(client, user, token):
    cpf = CPF().generate()
    client.post(
        '/client/',
        json={
            'name': 'bob',
            'email': 'bob@email.com',
            'cpf': cpf,
            'password': 'senhaatual',
        },
    )

    response = client.put(
        f'/client/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'bob2',
            'email': 'bob@email.com',
            'password': 'senhaatual',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_update_client_with_wrong_user(client, other_user, token):
    response = client.put(
        f'/client/{other_user.id}',
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
async def test_delete_client(client, user, token, session):
    response = client.delete(
        f'/client/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}

    deleted_user = await session.scalar(select(User).where(User.id == user.id))  # noqa

    assert deleted_user.is_deleted is True
    assert deleted_user.deleted_at is not None


@pytest.mark.asyncio
async def test_delete_client_with_wrong_user(
    client, other_user, token, session
):
    response = client.delete(
        f'/client/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}

    forbidden_user = await session.scalar(
        select(User).where(User.id == other_user.id)
    )  # noqa

    assert forbidden_user.is_deleted is False
    assert forbidden_user.deleted_at is None
