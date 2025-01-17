import json
from datetime import datetime
from typing import Union, Optional, List
from pydantic import BaseModel

from src.data.models.post_model import PostModel
from src.domain.entities.media import Media


class Post(BaseModel):
    id: Optional[str] = None
    content: Optional[str] = None
    user_id: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    medias: Optional[List[Media]] = None


    @classmethod
    def from_json(cls, json_data: Union[str, dict]):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        return Post(
            id=data.get('id'),
            content=data.get('content'),
            user_id=data.get('user_id'),
            location=data.get('location'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            created_date=data.get('created_date'),
            updated_date=data.get('updated_date'),
        )

    @classmethod
    def from_model(cls, post_model: PostModel):
        return cls(
            id=post_model.id,
            content=post_model.content,
            user_id=post_model.user_id,
            location=post_model.location,
            latitude=post_model.latitude,
            longitude=post_model.longitude,
            created_date=post_model.created_date,
            updated_date=post_model.updated_date
        )