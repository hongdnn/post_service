from functools import wraps

import jwt
from quart import request, jsonify

from src import Config


def token_required(required_user_info: bool = False):
    def decorator(f):
        @wraps(f)
        async def decorated(*args, **kwargs):
            token = request.headers.get('Authorization', '').split(" ")[-1]
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            if required_user_info:
                try:
                    user_info = decode_jwt(token)
                except ValueError as e:
                    return jsonify({'message': str(e)}), 401
                return await f(user_info, *args, **kwargs)
            else:
                return await f(*args, **kwargs)

        return decorated

    return decorator


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, Config.SOCIAL_SECRET_KEY, audience=Config.VALID_AUDIENCE, issuer=Config.VALID_ISSUER,
                          algorithms=[Config.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError('Token has expired')
    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')
