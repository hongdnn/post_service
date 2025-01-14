from sqlalchemy import Column, String, Text, TIMESTAMP, func, Float
from sqlalchemy.orm import relationship

from src.data.models.base import Base


class PostModel(Base):
    __tablename__ = 'posts'

    id = Column(String(36), primary_key=True)
    content = Column(Text)
    user_id = Column(String(24), nullable=False)
    location = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    created_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_date = Column(TIMESTAMP(timezone=True))

    # Define relationship with MediaModel
    medias = relationship("MediaModel", back_populates="post", lazy="joined")

