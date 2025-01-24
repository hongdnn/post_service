from sqlalchemy import Column, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship

from src.data.models.base import Base


class ReactionModel(Base):
    __tablename__ = 'reactions'

    id = Column(String(36), primary_key=True)
    post_id = Column(String(36), ForeignKey('posts.id'), nullable=False)
    user_id = Column(String(24), nullable=False)
    created_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    post = relationship("PostModel", back_populates="reactions")