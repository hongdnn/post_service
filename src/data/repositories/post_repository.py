from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select, func, column
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload

from src.data.models.post_model import PostModel
from src.data.models.reaction_model import ReactionModel
from src.domain.entities.media import Media
from src.domain.entities.post import Post


class PostRepositoryInterface(ABC):
    @abstractmethod
    async def create_post(self, post: Post) -> Post:
        pass

    @abstractmethod
    async def fetch_posts(self, request_user_id: str, user_ids: List[str], limit: int, recent_post_time: Optional[datetime] = None) ->list[Post]:
        pass

    @abstractmethod
    async def get_post_by_id(self, post_id: str) -> Optional[Post]:
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


    async def fetch_posts(self, request_user_id: str, user_ids: List[str], limit: int, recent_post_time: Optional[datetime] = None) ->list[Post]:
        async with self._session() as session:
            async with session.begin():
                # Subquery to get reaction counts
                reaction_subquery = (
                    select(
                        ReactionModel.post_id,
                        func.count(ReactionModel.id).label('reaction_count')
                    )
                    .group_by(ReactionModel.post_id)
                    .subquery()
                )

                # Subquery to check if the user who requests that reacted to a post
                user_reaction_count_subquery = (
                    select(
                        ReactionModel.post_id,
                        func.count(ReactionModel.id).label('user_reaction_count')
                    )
                    .filter(column(ReactionModel.user_id.key) == request_user_id)
                    .group_by(ReactionModel.post_id)
                    .subquery()
                )

                # Build the base query
                query = (
                    select(
                        PostModel,
                        func.coalesce(reaction_subquery.c.reaction_count, 0).label('reaction_count'),
                        func.coalesce(user_reaction_count_subquery.c.user_reaction_count, 0).label(
                            'user_reaction_count')
                    )
                    .options(joinedload(PostModel.medias))
                    .select_from(PostModel)
                    .outerjoin(reaction_subquery, column(PostModel.id.key) == reaction_subquery.c.post_id)
                    .outerjoin(user_reaction_count_subquery, column(PostModel.id.key) == user_reaction_count_subquery.c.post_id)
                    .where(PostModel.user_id.in_(user_ids))
                    .order_by(PostModel.created_date.desc())
                )
                if recent_post_time:
                    query = query.where(PostModel.created_date < recent_post_time)
                query = query.limit(limit)

                # Execute the query
                result = await session.execute(query)

                response = []
                for row in result.unique():
                    post = row[0]
                    post_data = Post.from_model(post)
                    # Add media data (empty list if no media)
                    post_data.medias = [Media.from_model(media) for media in post.medias] if post.medias else []
                    post_data.reaction_count = row[1]
                    post_data.is_reacted = row[2] > 0
                    response.append(post_data)

                return response

    async def get_post_by_id(self, post_id: str) -> Optional[Post]:
        async with self._session() as session:
            async with session.begin():
                statement = select(PostModel).where(column(PostModel.id.key) == post_id)
                result = await session.execute(statement)
                post_model = result.scalars().first()

                if not post_model:
                    return None

                return Post.from_model(post_model)