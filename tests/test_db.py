import pytest
from sqlalchemy import select
from validate_docbr import CPF

from project.models.base import Admin, Client, Role
from project.security import get_password_hash


@pytest.mark.asyncio
async def test_db_create_client(session, mock_db_time):
    with mock_db_time(model=Client) as time:
        cpf = CPF().generate()
        password_hash = get_password_hash('senha')
        new_user = Client(
            name='alice',
            cpf=cpf,
            email='teste@test',
            password=password_hash,
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(Client).where(Client.name == 'alice'))

    assert user.cpf == cpf
    assert user.created_at == time
    assert user.deleted_at is None
    assert user.is_deleted is False
    assert user.email == 'teste@test'
    assert user.id == 1
    assert user.name == 'alice'
    assert user.password == password_hash


@pytest.mark.asyncio
async def test_db_create_admin(session, mock_db_time):
    with mock_db_time(model=Admin) as time:
        cpf = CPF().generate()
        password_hash = get_password_hash('senha')
        new_user = Admin(
            name='alice',
            cpf=cpf,
            email='teste@test',
            password=password_hash,
            role=Role.ADMIN,
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(Admin).where(Admin.name == 'alice'))

    assert user.cpf == cpf
    assert user.created_at == time
    assert user.deleted_at is None
    assert user.is_deleted is False
    assert user.email == 'teste@test'
    assert user.id == 1
    assert user.name == 'alice'
    assert user.password == password_hash
