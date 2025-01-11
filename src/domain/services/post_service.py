import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
import re
from mypy_boto3_s3.client import S3Client

from src.data.repositories.media_repository import MediaRepositoryInterface
from src.data.repositories.post_repository import PostRepositoryInterface
from src.domain.entities.media import Media
from src.domain.entities.post import Post
from src import Config


class PostServiceInterface(ABC):
    @abstractmethod
    async def create_post(self, data: dict) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_presign_urls(self, files: list) -> Dict[str, Any]:
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


def generate_unique_key(file_name: str, folder: str) -> str:
    name_without_extension = re.sub(r'\.[^/.]+$', '', file_name)
    extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
    timestamp = datetime.now().timestamp()
    unique_id = str(uuid.uuid4())

    sanitized_name = re.sub(r'[^a-z0-9]+', '-', name_without_extension.lower())[:50]
    return f"{folder}/{sanitized_name}-{timestamp}-{unique_id}.{extension}"