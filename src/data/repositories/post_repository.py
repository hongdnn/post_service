from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload

from src.data.models.post_model import PostModel
from src.domain.entities.media import Media
from src.domain.entities.post import Post


class PostRepositoryInterface(ABC):
    @abstractmethod
    async def create_post(self, post: Post) -> Post:
        pass

    @abstractmethod
    async def fetch_posts(self, user_ids: List[str], limit: int, recent_post_time: Optional[datetime] = None) ->list[Post]:
        pass



class PostRepository(PostRepositoryInterface):
    def __init__(self, session: async_sessionmaker):
        self._session = session

    async def create_post(self, post: Post) -> Post:
        async with self._session() as session:
            async with session.begin():
                post_model = PostModel(
                    id = str(uuid4()),
                    content= post.content,
                    user_id = post.user_id,
                    location = post.location,
                    latitude = post.latitude,
                    longitude = post.longitude
                )
                session.add(post_model)
                await session.commit()
                return Post.from_model(post_model)


    async def fetch_posts(self, user_ids: List[str], limit: int, recent_post_time: Optional[datetime] = None) ->list[Post]:
        async with self._session() as session:
            async with session.begin():
                # Build the base query
                query = (
                    select(PostModel)
                    .options(joinedload(PostModel.medias))
                    .where(PostModel.user_id.in_(user_ids))
                    .order_by(PostModel.created_date.desc())
                )
                if recent_post_time:
                    query = query.where(PostModel.created_date < recent_post_time)

                query = query.limit(limit)

                # Execute the query
                result = await session.execute(query)

                posts = result.unique().scalars().all()

                response = []

                for post in posts:
                    post_data = Post.from_model(post)
                    # # Add media data (empty list if no media)
                    post_data.medias = [Media.from_model(media) for media in post.medias] if post.medias else []
                    response.append(post_data)

                return response