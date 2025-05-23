from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class DeleteMixin:
    deleted_at: Mapped[datetime] = mapped_column(
        init=False, default=None, nullable=True, index=True
    )
    is_deleted: Mapped[bool] = mapped_column(
        init=False, default=False, nullable=True, index=True
    )

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None


class CreateMixin:
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), index=True
    )


class UpdateMixin:
    updated_at: Mapped[datetime] = mapped_column(
        init=False, default=None, nullable=True, index=True
    )
    is_updated: Mapped[bool] = mapped_column(
        init=False, default=False, nullable=True, index=True
    )

    def update(self):
        self.is_updated = True
        self.updated_at = datetime.now()


class BaseMixins(CreateMixin, UpdateMixin, DeleteMixin):
    pass
