import enum
from datetime import datetime
from typing import List

from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, String, Table
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

from project.utils.mixins import BaseMixins


class OrderStatus(enum.Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELED = 'canceled'


class Section(enum.Enum):
    HIGIENE = 'higiene'
    ALIMENTACAO = 'alimentacao'
    VESTUARIO = 'vestuario'


class Role(enum.Enum):
    ADMIN = 'admin'
    CLIENT = 'client'


class Base(DeclarativeBase):
    pass


order_products_association_table = Table(
    'orders_products',
    Base.metadata,
    Column('product_id', ForeignKey('products.id')),
    Column('order_id', ForeignKey('orders.id')),
)


class User(AbstractConcreteBase, Base):
    pass


class Client(MappedAsDataclass, User, BaseMixins):
    __tablename__ = 'clients'
    __mapper_args__ = {
        'polymorphic_identity': 'client',
        'concrete': True,
    }

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    cpf: Mapped[str] = mapped_column(String(11), unique=True)
    role: Mapped[str] = mapped_column(Enum(Role), default=Role.CLIENT)

    orders: Mapped[List['Order']] = relationship(
        'Order', back_populates='client', init=False
    )


class Admin(MappedAsDataclass, User, BaseMixins):
    __tablename__ = 'admins'
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
        'concrete': True,
    }

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    cpf: Mapped[str] = mapped_column(String(11), unique=True)
    role: Mapped[str] = mapped_column(Enum(Role), default=Role.ADMIN)


class Order(MappedAsDataclass, Base, BaseMixins):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.id'))
    client: Mapped['Client'] = relationship('Client', back_populates='orders')  # type: ignore
    products: Mapped[List['Product']] = relationship(
        'Product', secondary='orders_products', back_populates='orders'
    )

    total: Mapped[float] = mapped_column(default=0.0)
    status: Mapped[str] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING
    )


class Product(MappedAsDataclass, Base, BaseMixins):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[float]
    barcode: Mapped[str] = mapped_column(String(12))
    section: Mapped[str] = mapped_column(Enum(Section))
    stock: Mapped[int] = mapped_column(
        CheckConstraint('stock >= 0', name='check_stock_gte_zero')
    )
    expiration_date: Mapped[datetime]

    orders: Mapped[List['Order']] = relationship(  # type: ignore
        'Order',
        secondary='orders_products',
        back_populates='products',
        init=False,
    )


Base.registry.configure()
