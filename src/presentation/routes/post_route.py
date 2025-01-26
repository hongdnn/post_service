from datetime import datetime

import aiohttp
from dependency_injector.wiring import inject, Provide
from quart import Blueprint, request, jsonify
from marshmallow import ValidationError

from src import Config
from src.infrastructure.dependency_container import Container
from src.domain.services.post_service import PostService
from src.infrastructure.jwt_handler import token_required

from src.presentation.schemas.post_schema import CreatePostSchema

post_bp = Blueprint('post', __name__, url_prefix='/posts')

create_post_schema = CreatePostSchema()

@post_bp.route('', methods=['POST'])
@token_required(required_user_info=True)
@inject
async def create_post(user_info: dict, post_service: PostService = Provide[Container.post_service]):
    """Create a new post."""
    try:
        data = await request.get_json()
        """Validate request data"""
        create_post_schema.load(data)
        data['user_id'] = user_info['id']

        response = await post_service.create_post(data)
        return jsonify(response), 200 if response.get('status') == 0 else 500
    except ValidationError as err:
        return jsonify({"error": "Validation failed",  "status": 1, "messages": err.messages}), 400

    except ValueError as ve:
        return jsonify({"error": "ValueError occurred",  "status": 1, "message": str(ve)}), 400

@post_bp.route('/presign', methods=['POST'])
@token_required()
@inject
async def create_presign_urls(post_service: PostService = Provide[Container.post_service]):
    """Generate presign urls to upload media files to S3."""
    try:
        data = await request.get_json()
        files = data['files']
        response = await post_service.generate_presign_urls(files)
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": "Some error occurred",  "status": 1, "message": str(e)}), 500

@post_bp.route('', methods=['GET'])
@token_required(required_user_info=True)
@inject
async def fetch_posts(user_info: dict, post_service: PostService = Provide[Container.post_service]):
    """Fetch list of post."""
    try:
        size = request.args.get('size', default=10, type=int)
        date_str = request.args.get('date', type=str)
        date = None
        if date_str:
            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError as e:
                return jsonify({"error": "Invalid date format", "status": 1, "message": str(e)}), 400

        """Call chat service to get followees """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{Config.CHAT_SERVICE_BASE_URL}/follows/followees",
                headers={
                    "Authorization": request.headers.get('Authorization')
                }
                ) as followee_response:

                    if followee_response.status == 200:
                        followee_data = await followee_response.json()
                        followee_ids = followee_data.get('data', [])
                        followee_ids.append(user_info['id'])
                        response = await post_service.fetch_posts(user_info['id'], followee_ids, size, date)
                        if response.get('status') != 0:
                            return jsonify(response), 500

                        """Call chat service to get user info in each post """
                        user_ids_set = {post['user_id'] for post in response['data']}
                        async with session.post(
                                f"{Config.CHAT_SERVICE_BASE_URL}/users/posts",
                                json={"user_ids": list(user_ids_set)},
                                headers={"Authorization": request.headers.get('Authorization')}
                        ) as user_response:
                            if user_response.status != 200:
                                return jsonify({"status": 1, "message": "Failed to fetch user information"}), 500

                            user_data = await user_response.json()
                            user_map = {user['_id']: user for user in user_data.get('data', [])}


                        for post in response['data']:
                            user_info = user_map.get(post['user_id'], {})
                            post['user'] = user_info

                        return jsonify(response), 200


        return jsonify({
            "status": 1,
            "message": "An error occurred",
        }), followee_response.status


    except Exception as error:
        return jsonify({
            "error": str(error),
            "status": 1,
            "message": "An error occurred"
        }), 400


@post_bp.route('/profile', methods=['GET'])
@token_required(required_user_info=True)
@inject
async def fetch_profile_posts(user_info: dict, post_service: PostService = Provide[Container.post_service]):
    """Fetch list of posts in a user profile."""
    try:
        size = request.args.get('size', default=10, type=int)
        user_id = request.args.get('user_id', type=str)
        date_str = request.args.get('date', type=str)
        date = None
        if date_str:
            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError as e:
                return jsonify({"error": "Invalid date format", "status": 1, "message": str(e)}), 400

        response = await post_service.fetch_posts(user_info['id'], [user_id], size, date)
        if response.get('status') != 0:
            return jsonify(response), 500

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{Config.CHAT_SERVICE_BASE_URL}/users/posts",
                    json={"user_ids": [user_id]},
                    headers={"Authorization": request.headers.get('Authorization')}
            ) as user_response:
                if user_response.status != 200:
                    return jsonify({"status": 1, "message": "Failed to fetch user information"}), 500

                user_data = await user_response.json()
                user_map = {user['_id']: user for user in user_data.get('data', [])}

                for post in response['data']:
                    user_info = user_map.get(post['user_id'], {})
                    post['user'] = user_info

                return jsonify(response), 200

    except Exception as error:
        return jsonify({
            "error": str(error),
            "status": 1,
            "message": "An error occurred"
        }), 400