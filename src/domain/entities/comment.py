import json
from datetime import datetime
from typing import Union, Optional
from pydantic import BaseModel
from src.data.models.comment_model import CommentModel


class Comment(BaseModel):
    id: Optional[str] = None
    content: str
    post_id: str
    user_id: str
    replied_comment_id: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None

    @classmethod
    def from_orm(cls, json_data: Union[str, dict]):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        return Comment(
            id = data.get('id'),
            content=data.get('content'),
            post_id=data.get('post_id'),
            user_id=data.get('user_id'),
            replied_comment_id=data.get('replied_comment_id'),
            created_date=data.get('created_date'),
            updated_date=data.get('updated_date'),
        )

    @classmethod
    def from_model(cls, comment_model: CommentModel):
        return cls(
            id=comment_model.id,
            content=comment_model.content,
            post_id=comment_model.post_id,
            user_id=comment_model.user_id,
            replied_comment_id=comment_model.replied_comment_id,
            created_date=comment_model.created_date,
            updated_date=comment_model.updated_date
        )