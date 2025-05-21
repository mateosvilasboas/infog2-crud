import enum
from datetime import datetime
from sqlalchemy import (
    String, 
    Enum,
    CheckConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from .base import Base


class Section(enum.Enum):
    HIGIENE = "higiene"
    ALIMENTACAO = "alimentacao"
    VESTUARIO = "vestuario"

class Product(Base):
    __tablename__ = "products"
    
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[float]
    barcode: Mapped[str] = mapped_column(
        String(12)
    )
    section: Mapped[str] = mapped_column(
        Enum(Section)
    )
    stock: Mapped[int] = mapped_column(
        CheckConstraint(
            "stock >= 0",
            name="check_stock_gte_zero"
        )
    )
    expiration_date: Mapped[datetime]
