import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any

from sqlalchemy.exc import IntegrityError

from src.constants.notification_type import NotificationType
from src.data.repositories.post_repository import PostRepositoryInterface
from src.data.repositories.reaction_repository import ReactionRepositoryInterface
from src.domain.entities.reaction import Reaction
from src.infrastructure.kafka.notification_kafka_producer import NotificationKafkaProducer


class ReactionServiceInterface(ABC):
    @abstractmethod
    async def update_reaction(self, data: dict) -> Dict[str, Any]:
        pass



class ReactionService(ReactionServiceInterface):
    def __init__(self, reaction_repository: ReactionRepositoryInterface, post_repository: PostRepositoryInterface,
                          notification_kafka_producer: NotificationKafkaProducer):
        self._reaction_repository = reaction_repository
        self._post_repository = post_repository
        self._notification_kafka_producer = notification_kafka_producer

    async def update_reaction(self, data: dict) -> Dict[str, Any]:
        try:
            status, reaction = await self._reaction_repository.update_reaction(data)
            if status:
                """Fetch the post and send notification asynchronously."""
                asyncio.create_task(self.fetch_and_notify(reaction))
                return {'status': 0, 'message': 'React success'}
            return { 'status': 0, 'message': 'Remove reaction success' }
        except IntegrityError:
            return {"status": 2, "messages": "Invalidate data"}
        except Exception as e:
            print(e)
            return {'status': 1, 'message': "There's something wrong"}

    async def fetch_and_notify(self, reaction: Reaction):
        try:
            post = await self._post_repository.get_post_by_id(reaction.post_id)
            if post:
                await self._notification_kafka_producer.post_message(post.user_id, reaction, NotificationType.REACTION)
        except Exception as e:
            print(f"Error in sending kafka message: {e}")
