import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
from wsgiref.headers import Headers

import aiohttp
from mypy_boto3_s3.client import S3Client

from src.data.repositories.media_repository import MediaRepositoryInterface
from src.data.repositories.post_repository import PostRepositoryInterface
from src.domain.entities.post import Post
from src import Config


class PostServiceInterface(ABC):
    @abstractmethod
    async def create_post(self, data: dict) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_presign_urls(self, files: list) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def fetch_posts(self, user_id: str, followee_ids: List[str], size: int, date: Optional[datetime] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_post_detail(self, user_id: str, post_id: str, headers: Headers) -> Dict[str, Any]:
        pass


class PostService(PostServiceInterface):

    def __init__(self, post_repository: PostRepositoryInterface, media_repository: MediaRepositoryInterface, s3_client: S3Client):
        self._post_repository = post_repository
        self._media_repository = media_repository
        self.s3_client = s3_client

    async def create_post(self, data: dict) -> Dict[str, Any]:
        try:
            medias = data.pop('medias', [])
            post = Post.from_json(data)
            response = await self._post_repository.create_post(post)
            if len(medias) > 0:
                await self._media_repository.create_medias(response.id, medias)
            return {"data": response.model_dump(), "status": 0, "message": "Create post success"}
        except Exception as e:
            print(f"Error: {e}")
            return {"data": None, "status": 1, "message": "There's something wrong"}

    async def generate_presign_urls(self, files: list) -> Dict[str, Any]:
        try:
            response_data = []
            for file in files:
                key = generate_unique_key(file['file_name'], 'posts')
                url = self.s3_client.generate_presigned_url(
                    'put_object',
                    Params={
                        'Bucket': Config.AWS_BUCKET_NAME,
                        'Key': key,
                        'ContentType': file['type'],
                        'ACL': 'public-read'
                    },
                    ExpiresIn=3600
                )
                response_data.append({"key": key, "url": url})
            return {"data": response_data, "status": 0, "message": "Generate presign urls success"}
        except Exception as e:
            print(f"Error: {e}")
            return {"data": None, "status": 1, "message": "There's something wrong"}

    async def fetch_posts(self, user_id: str, followee_ids: List[str], size: int, date: Optional[datetime] = None) -> Dict[str, Any]:
        try:
            response = await self._post_repository.fetch_posts(user_id, followee_ids, size, date)
            posts_data = [post.model_dump() for post in response]  # Convert each Post to a dictionary
            return {"data": posts_data, "status": 0, "message": "Fetch posts success"}
        except Exception as e:
            print(f"Error: {e}")
            return {"data": None, "status": 1, "message": "There's something wrong"}

    async def get_post_detail(self, user_id: str, post_id: str, headers: Headers) -> Dict[str, Any]:
        try:
            response = await self._post_repository.get_post_detail(user_id, post_id)
            if response is None:
                return {"data": None, "status": 2, "message": "Post not found"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{Config.CHAT_SERVICE_BASE_URL}/users/posts",
                        json={"user_ids": [response.user_id]},
                        headers={"Authorization": headers.get('Authorization')}
                ) as user_response:
                    if user_response.status != 200:
                        return {"data": None, "status": 2, "message": "Failed to fetch user information"}

                    user_data = await user_response.json()
                    users = user_data.get('data', [])
                    if not users:
                        return {"data": None, "status": 2, "message": "Failed to fetch user information"}

                    post = response.model_dump()
                    post['user'] = users[0]
                    return {"data": post, "status": 0, "message": "Fetch post success"}
        except Exception as e:
            print(f"Error: {e}")
            return {"data": None, "status": 1, "message": "There's something wrong"}


def generate_unique_key(file_name: str, folder: str) -> str:
    name_without_extension = re.sub(r'\.[^/.]+$', '', file_name)
    extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
    timestamp = datetime.now().timestamp()
    unique_id = str(uuid.uuid4())

    sanitized_name = re.sub(r'[^a-z0-9]+', '-', name_without_extension.lower())[:50]
    return f"{folder}/{sanitized_name}-{timestamp}-{unique_id}.{extension}"