from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column


class SoftDeleteMixin:
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


class BaseMixins(SoftDeleteMixin):
    pass
