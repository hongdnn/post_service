import asyncio
from abc import abstractmethod, ABC
from typing import Dict, Any
from wsgiref.headers import Headers

import aiohttp
from sqlalchemy.exc import IntegrityError

from src import Config
from src.constants.notification_type import NotificationType
from src.data.repositories.comment_repository import CommentRepositoryInterface
from src.data.repositories.post_repository import PostRepositoryInterface
from src.domain.entities.comment import Comment
from src.infrastructure.kafka.notification_kafka_producer import NotificationKafkaProducer


class CommentServiceInterface(ABC):
    @abstractmethod
    async def create_comment(self, data: dict) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def fetch_comments(self, post_id: str, size: int, page: int, headers: Headers) -> Dict[str, Any]:
        pass



class CommentService(CommentServiceInterface):
    def __init__(self, comment_repository: CommentRepositoryInterface, post_repository: PostRepositoryInterface,
                          notification_kafka_producer: NotificationKafkaProducer):
        self._comment_repository = comment_repository
        self._post_repository = post_repository
        self._notification_kafka_producer = notification_kafka_producer

    async def create_comment(self, data: dict) -> Dict[str, Any]:
        try:
            response = await self._comment_repository.create_comment(data)
            asyncio.create_task(self.notify_comment(response))
            return {'data': response.model_dump(), 'status': 0, 'message': 'Create comment success' }
        except IntegrityError:
            return {"status": 2, "messages": "Invalidate data"}
        except Exception as e:
            print(e)
            return {'status': 1, 'message': "There's something wrong" }

    async def notify_comment(self, comment: Comment):
        try:
            post = await self._post_repository.get_post_by_id(comment.post_id)
            if post and post.user_id != comment.user_id:
                notification_type = (
                    NotificationType.REPLY_COMMENT
                    if comment.replied_comment_id is not None
                    else NotificationType.COMMENT
                )
                await self._notification_kafka_producer.post_message(
                    post.user_id,
                    comment,
                    notification_type
                )
        except Exception as e:
            print(f"Error in sending kafka message: {e}")

    async def fetch_comments(self, post_id: str, size: int, page: int, headers: Headers) -> Dict[str, Any]:
        try:
            comments = await self._comment_repository.fetch_comments(post_id, size, page)
            comments_data = [comment.model_dump() for comment in comments]
            if len(comments_data) > 0:
                """Call chat service to get user who commented """
                user_ids_set = {comment.user_id for comment in comments}
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                            f"{Config.CHAT_SERVICE_BASE_URL}/users/posts",
                            json={"user_ids": list(user_ids_set)},
                            headers={"Authorization": headers.get('Authorization')}
                    ) as user_response:
                        if user_response.status != 200:
                            return {"status": 1, "message": "Failed to fetch user information"}

                        user_data = await user_response.json()
                        user_map = {user['_id']: user for user in user_data.get('data', [])}

                for comment in comments_data:
                    user_info = user_map.get(comment['user_id'], {})
                    comment['user'] = user_info

            return { "data": comments_data, "status": 0, "message": "Fetch comments success" }

        except Exception as e:
            print(f"Error: {e}")
            return {"data": None, "status": 1, "message": "There's something wrong"}