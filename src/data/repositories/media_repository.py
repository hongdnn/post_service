from abc import abstractmethod, ABC
from uuid import uuid4

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.data.models.media_model import MediaModel


class MediaRepositoryInterface(ABC):
    @abstractmethod
    async def create_medias(self, post_id: str, medias: list[dict]):
        pass

class MediaRepository(MediaRepositoryInterface):
    def __init__(self, session: async_sessionmaker):
        self._session = session

    async def create_medias(self, post_id: str, medias: list[dict]):
        async with self._session() as session:
            async with session.begin():
                for media in medias:
                    media_model = MediaModel(
                        id=str(uuid4()),
                        post_id=post_id,  # Link to the post
                        media_type=media['media_type'],
                        media_url=media['media_url'],
                        file_size=media['file_size'],
                        file_name=media['file_name'],
                        mime_type=media['mime_type'],
                        width=media['width'],
                        height=media['height'],
                        video_duration=media.get('video_duration'),
                        video_frame_rate=media.get('video_frame_rate')
                    )
                    session.add(media_model)
                await session.commit()