from abc import abstractmethod, ABC
from uuid import uuid4

from sqlalchemy import delete, and_, select, column
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.data.models.reaction_model import ReactionModel

class ReactionRepositoryInterface(ABC):
    @abstractmethod
    async def update_reaction(self, reaction: dict) -> bool:
        pass

class ReactionRepository(ReactionRepositoryInterface):
    def __init__(self, session: async_sessionmaker):
        self._session = session

    async def update_reaction(self, reaction: dict) -> bool:
        async with self._session() as session:
            async with session.begin():
                statement = select(ReactionModel).where(
                    and_(
                        ReactionModel.post_id == reaction['post_id'],
                        ReactionModel.user_id == reaction['user_id']
                    )
                )
                result = await session.execute(statement)
                existing_reaction = result.scalars().first()

                if existing_reaction:
                    # If it exists, delete the reaction
                    delete_statement = delete(ReactionModel).where(
                        column(ReactionModel.id.key) == existing_reaction.id
                    )
                    await session.execute(delete_statement)
                    return False  # Indicating that the reaction was deleted

                else:
                    # If it does not exist, create a new record
                    create_statement = ReactionModel(
                        id=str(uuid4()),
                        post_id=reaction['post_id'],
                        user_id=reaction['user_id'],
                    )
                    await session.merge(create_statement)
                    return True