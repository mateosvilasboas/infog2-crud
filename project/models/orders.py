from typing import List
from sqlalchemy import (
    ForeignKey
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from .base import Base
from .products import Product
from .users import User


class Order(Base):
    __tablename__ = "orders"

    client_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )
    client: Mapped[User] = relationship()
    products: Mapped[List["Product"]] = relationship(
        secondary="orders_products"
    )

