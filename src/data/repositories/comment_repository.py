from abc import abstractmethod, ABC
from uuid import uuid4

from sqlalchemy import select, column
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.data.models.comment_model import CommentModel
from src.domain.entities.comment import Comment


class CommentRepositoryInterface(ABC):
    @abstractmethod
    async def create_comment(self, comment: dict) -> Comment:
        pass

    @abstractmethod
    async def fetch_comments(self, post_id: str, limit: int, page: int) -> list[Comment]:
        pass

class CommentRepository(CommentRepositoryInterface):


    def __init__(self, session: async_sessionmaker):
        self._session = session

    async def create_comment(self, comment: dict) -> Comment:
        async with self._session() as session:
            async with session.begin():
                comment_model = CommentModel(
                    id=str(uuid4()),
                    content=comment['content'],
                    post_id=comment['post_id'],
                    user_id=comment['user_id'],
                    replied_comment_id=comment['replied_comment_id'],
                )
                session.add(comment_model)
                await session.flush()
                return Comment.from_model(comment_model)


    async def fetch_comments(self, post_id: str, limit: int, page: int) -> list[Comment]:
        async with self._session() as session:
            async with session.begin():
                print(post_id, page, limit)
                query = (
                    select(CommentModel)
                    .where(CommentModel.post_id.__eq__(post_id))
                    .limit(limit)
                    .offset((page - 1) * limit)
                )

                result = await session.execute(query)
                print('list comments:', result)
                comment_models = result.scalars().all()
                return [Comment.from_model(model) for model in comment_models]