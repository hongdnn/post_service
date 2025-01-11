from datetime import datetime
import json
from typing import Union, Optional

from pydantic import BaseModel

from src.data.models.media_model import MediaModel


class Media(BaseModel):
    id: str
    post_id: str
    media_type: int
    media_url: str
    file_size: float
    file_name: Optional[str] = None
    mime_type: str
    created_date: Optional[datetime] = None
    width: int
    height: int
    video_duration: Optional[int] = None
    video_frame_rate: Optional[int] = None

    @classmethod
    def from_json(cls, json_data: Union[str, dict]):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        return Media(
            id=data.get('id'),
            post_id=data.get('post_id'),
            media_type=data.get('media_type'),
            media_url=data.get('media_url'),
            file_size=data.get('file_size'),
            file_name=data.get('file_name'),
            mime_type=data.get('mime_type'),
            created_date=data.get('created_date'),
            width=data.get('width'),
            height=data.get('height'),
            video_duration=data.get('video_duration'),
            video_frame_rate=data.get('video_frame_rate'),
        )

    @classmethod
    def from_model(cls, media_model: MediaModel):
        return cls(
            id=media_model.id,
            post_id=media_model.post_id,
            media_type=media_model.media_type,
            media_url=media_model.media_url,
            file_size=media_model.file_size,
            file_name=media_model.file_name,
            mime_type=media_model.mime_type,
            created_date=media_model.created_date,
            width=media_model.width,
            height=media_model.height,
            video_duration=media_model.video_duration,
            video_frame_rate=media_model.created_date,
        )

