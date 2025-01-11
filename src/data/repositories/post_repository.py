from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.data.models.post_model import PostModel
from src.domain.entities.post import Post


class PostRepositoryInterface(ABC):
    @abstractmethod
    async def create_post(self, post: Post) -> Post:
        pass

    @abstractmethod
    async def fetch_posts(self, limit: int, recent_post_time: datetime) ->list[Post]:
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


    async def fetch_posts(self, limit: int, recent_post_time: datetime) ->list[Post]:
        pass