from dependency_injector.wiring import inject, Provide
from quart import Blueprint, request, jsonify
from marshmallow import ValidationError

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
