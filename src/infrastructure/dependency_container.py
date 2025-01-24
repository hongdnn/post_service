from dependency_injector import containers, providers
from boto3 import client as boto3_client
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src import Config
from src.data.repositories.media_repository import MediaRepository
from src.data.repositories.post_repository import PostRepository
from src.data.repositories.reaction_repository import ReactionRepository
from src.domain.services.post_service import PostService
from src.domain.services.reaction_service import ReactionService


class Container(containers.DeclarativeContainer):

    # Database configuration
    config = providers.Configuration()
    engine = providers.Singleton(
        create_async_engine,
        Config.SQLALCHEMY_DATABASE_URI,
        echo=True,
        future=True
    )

    # Asynchronous session factory
    async_session = providers.Singleton(
        async_sessionmaker,
        bind=engine,  # You use the engine here
        class_=AsyncSession,
        expire_on_commit=False
    )

    # S3 client provider
    s3_client = providers.Singleton(
        boto3_client,
  "s3",
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    )

    post_repository = providers.Factory(
        PostRepository,
        session=async_session
    )

    media_repository = providers.Factory(
        MediaRepository,
        session=async_session
    )

    reaction_repository = providers.Factory(
        ReactionRepository,
        session=async_session
    )

    post_service = providers.Factory(
        PostService,
        post_repository=post_repository,
        media_repository=media_repository,
        s3_client= s3_client
    )

    reaction_service = providers.Factory(
        ReactionService,
        reaction_repository=reaction_repository
    )