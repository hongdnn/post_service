from abc import abstractmethod, ABC
from typing import Optional
from uuid import uuid4

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.data.models.reaction_model import ReactionModel
from src.domain.entities.reaction import Reaction


class ReactionRepositoryInterface(ABC):
    @abstractmethod
    async def update_reaction(self, reaction: dict) -> (bool, Optional[Reaction]):
        pass

class ReactionRepository(ReactionRepositoryInterface):
    def __init__(self, session: async_sessionmaker):
        self._session = session

    async def update_reaction(self, reaction: dict) -> (bool, Optional[Reaction]):
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
                    await session.delete(existing_reaction)
                    return False, None  # Indicating that the reaction was deleted

                else:
                    # If it does not exist, create a new record
                    reaction_model = ReactionModel(
                        id=str(uuid4()),
                        post_id=reaction['post_id'],
                        user_id=reaction['user_id'],
                    )
                    session.add(reaction_model)
                    # Ensure that the reaction gets flushed and committed to the database
                    await session.flush()
                    return True, Reaction.from_model(reaction_model)