from abc import ABC, abstractmethod
from typing import Dict, Any

from sqlalchemy.exc import IntegrityError

from src.data.repositories.reaction_repository import ReactionRepositoryInterface


class ReactionServiceInterface(ABC):
    @abstractmethod
    async def update_reaction(self, data: dict) -> Dict[str, Any]:
        pass



class ReactionService(ReactionServiceInterface):
    def __init__(self, reaction_repository: ReactionRepositoryInterface):
        self._reaction_repository = reaction_repository

    async def update_reaction(self, data: dict) -> Dict[str, Any]:
        try:
            response = await self._reaction_repository.update_reaction(data)
            if response:
                return {'status': 0, 'message': 'React success'}
            return { 'status': 0, 'message': 'Remove reaction success' }
        except IntegrityError:
            return {"status": 2, "messages": "Invalidate data"}
        except Exception as e:
            print(e)
            return {'status': 1, 'message': "There's something wrong"}
