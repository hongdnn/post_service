import json
from datetime import datetime
from typing import Union

from pydantic import BaseModel

from src.data.models.reaction_model import ReactionModel


class Reaction(BaseModel):
    id: str
    post_id: str
    user_id: str
    created_date: datetime

    @classmethod
    def from_orm(cls, json_data: Union[str, dict]):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        return Reaction(
            id = data.get('id'),
            post_id=data.get('post_id'),
            user_id=data.get('user_id'),
            created_date=data.get('created_date'),
        )

    @classmethod
    def from_model(cls, media_model: ReactionModel):
        return cls(
            id=media_model.id,
            post_id=media_model.post_id,
            user_id=media_model.user_id,
            created_date=media_model.created_date
        )