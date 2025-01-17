import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOCIAL_SECRET_KEY = os.getenv('SOCIAL_SECRET_KEY')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
    VALID_ISSUER = os.getenv('VALID_ISSUER')
    VALID_AUDIENCE = os.getenv('VALID_AUDIENCE')
    DEBUG = os.getenv('ENV', 'development') == 'development'
    AWS_REGION = os.getenv('AWS_REGION')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
    CHAT_SERVICE_BASE_URL = os.getenv('CHAT_SERVICE_BASE_URL')
    FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL')
