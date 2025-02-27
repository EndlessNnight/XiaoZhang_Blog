from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from ..core.database import Base
from .mixins import SoftDeleteMixin

class Comment(Base, SoftDeleteMixin):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    # 关系
    article = relationship("Article", back_populates="comments")
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", 
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan") 