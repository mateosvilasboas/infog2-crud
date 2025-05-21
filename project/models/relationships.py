from sqlalchemy import (
    ForeignKey
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from .base import Base
from .products import Product
from .users import User


class OrderProduct(Base):
    __tablename__ = "orders_products"
    
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(default=1)