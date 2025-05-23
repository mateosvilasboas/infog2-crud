from http import HTTPStatus

import pytest
from sqlalchemy import and_, select
from validate_docbr import CPF

from project.models.base import Role, User


def test_admin_create_client(client, admin_token):
    """Test admin creating a new client user."""
    password = 'senha123'
    cpf = CPF().generate()
    response = client.post(
        '/admin/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'cpf': cpf,
            'password': password,
            'role': 'client',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'name': 'alice',
        'email': 'alice@example.com',
        'cpf': cpf,
        'id': response.json()['id'],
        'role': Role.CLIENT.value,
    }


def test_admin_create_admin(client, admin_token):
    """Test admin creating a new admin user."""
    password = 'senha123'
    cpf = CPF().generate()
    response = client.post(
        '/admin/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'name': 'bob',
            'email': 'bob@example.com',
            'cpf': cpf,
            'password': password,
            'role': 'admin',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'name': 'bob',
        'email': 'bob@example.com',
        'cpf': cpf,
        'id': response.json()['id'],
        'role': Role.ADMIN.value,
    }


def test_admin_create_user_invalid_role(client, admin_token):
    """Test admin attempting to create user with invalid role."""
    cpf = CPF().generate()
    response = client.post(
        '/admin/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'cpf': cpf,
            'password': 'senha123',
            'role': 'invalid',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Role does not exist'}


def test_admin_create_user_existing_email(client, admin_token):
    """Test admin attempting to create user with existing email."""
    cpf1 = CPF().generate()
    cpf2 = CPF().generate()

    client.post(
        '/admin/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'cpf': cpf1,
            'password': 'senha123',
            'role': 'client',
        },
    )

    response = client.post(
        '/admin/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'name': 'bob',
            'email': 'alice@example.com',
            'cpf': cpf2,
            'password': 'senha456',
            'role': 'client',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_admin_create_user_existing_cpf(client, admin_token):
    """Test admin attempting to create user with existing CPF."""
    cpf = CPF().generate()

    client.post(
        '/admin/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'cpf': cpf,
            'password': 'senha123',
            'role': 'client',
        },
    )

    response = client.post(
        '/admin/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'name': 'bob',
            'email': 'bob@example.com',
            'cpf': cpf,
            'password': 'senha456',
            'role': 'client',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'CPF already exists'}


def test_admin_create_user_unauthorized_client(client, token):
    """Test that a client cannot create users."""
    cpf = CPF().generate()
    response = client.post(
        '/admin/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'alice',
            'email': 'alice@example.com',
            'cpf': cpf,
            'password': 'senha123',
            'role': 'client',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not enough permissions'}


def test_admin_get_users(client, admin_token):
    """Test getting all users as admin."""
    response = client.get(
        '/admin/', headers={'Authorization': f'Bearer {admin_token}'}
    )

    users = response.json()['users']
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': users}


def test_admin_get_users_with_email_filter(client, admin_token, user):
    """Test filtering users by email."""
    response = client.get(
        '/admin/',
        params={'email': user.email},
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    users = response.json()['users']
    assert len(users) == 1
    assert users[0]['email'] == user.email


def test_admin_get_users_with_name_filter(client, admin_token, user):
    """Test filtering users by name."""
    response = client.get(
        '/admin/',
        params={'name': user.name},
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    users = response.json()['users']
    assert len(users) == 1
    assert users[0]['name'] == user.name


def test_admin_get_users_with_pagination(client, admin_token):
    """Test pagination parameters."""
    response = client.get(
        '/admin/',
        params={'limit': 1, 'offset': 0},
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    users = response.json()['users']
    assert len(users) <= 1


def test_admin_get_users_unauthorized_client(client, token):
    """Test that a client cannot get user list."""
    response = client.get(
        '/admin/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not enough permissions'}


@pytest.mark.asyncio
async def test_admin_delete_user(client, user, admin_token, session):
    """Test admin deleting a user."""
    response = client.delete(
        f'/admin/{user.id}',
        params={'role': 'client'},
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}

    deleted_user = await session.scalar(
        select(User).where(and_(User.id == user.id, User.role == Role.CLIENT))
    )
    assert deleted_user.is_deleted is True


@pytest.mark.asyncio
async def test_admin_delete_user_already_deleted(
    client, user, admin_token, session
):
    """Test deleting an already deleted user."""
    response = client.delete(
        f'/admin/{user.id}',
        params={'role': 'client'},
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}

    response = client.delete(
        f'/admin/{user.id}',
        params={'role': 'client'},
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'User already deleted'}


def test_admin_delete_user_unauthorized_client(client, token, user):
    """Test that a client cannot delete users."""
    response = client.delete(
        f'/admin/{user.id}',
        params={'role': 'client'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not enough permissions'}


def test_admin_delete_nonexistent_user(client, admin_token):
    """Test deleting a user that doesn't exist."""
    response = client.delete(
        '/admin/99999',
        params={'role': 'client'},
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
