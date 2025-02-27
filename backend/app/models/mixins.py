from sqlalchemy import Boolean, DateTime, Column
from datetime import datetime

class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True) 