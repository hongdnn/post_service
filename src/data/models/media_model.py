from enum import IntEnum
from sqlalchemy import Column, String, Integer, CheckConstraint, Text, Float, TIMESTAMP, func, ForeignKey
from src.data.models.base import Base

class MediaType(IntEnum):
    IMAGE = 0
    VIDEO = 1



class MediaModel(Base):
    __tablename__ = 'medias'

    id = Column(String(73), primary_key=True)
    post_id = Column(String(36), ForeignKey('posts.id'), nullable=False)
    media_type = Column(Integer, nullable=False)
    media_url = Column(Text, nullable=False)
    file_size = Column(Float, nullable=False)
    file_name = Column(Text, nullable=False)
    mime_type = Column(String(50), nullable=False)
    created_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    video_duration = Column(Integer)
    video_frame_rate = Column(Integer)


    # Add constraint to ensure only valid enum values
    __table_args__ = (
        CheckConstraint(
            media_type.in_([member.value for member in MediaType]),
            name='check_valid_media_type'
        ),
    )
