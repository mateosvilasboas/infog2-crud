import enum
from sqlalchemy import func, Enum, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from .base import Base


class Role(enum.Enum):
    ADMIN = "admin"
    CLIENT = "client"


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    password: Mapped[str]
    cpf: Mapped[str] = mapped_column(
        String(11),
        unique=True
    )
    role: Mapped[str] = mapped_column(
        Enum(Role),
        default=Role.CLIENT
    )

    
