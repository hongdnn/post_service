from sqlalchemy import Column, String, TIMESTAMP, func, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.data.models.base import Base


class CommentModel(Base):
    __tablename__ = 'comments'

    id = Column(String(36), primary_key=True)
    content = Column(Text, nullable=False)
    post_id = Column(String(36), ForeignKey('posts.id'), nullable=False)
    user_id = Column(String(24), nullable=False)
    replied_comment_id = Column(String(36), ForeignKey('comments.id'))
    created_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_date = Column(TIMESTAMP(timezone=True))

    post = relationship("PostModel", back_populates="comments")