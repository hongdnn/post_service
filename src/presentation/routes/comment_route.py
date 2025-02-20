from dependency_injector.wiring import Provide, inject
from marshmallow import ValidationError
from quart import Blueprint, request, jsonify

from src import Container
from src.domain.services.comment_service import CommentServiceInterface
from src.infrastructure.jwt_handler import token_required
from src.presentation.schemas.comment_schema import CreateCommentSchema, FetchCommentsSchema

comment_bp = Blueprint('comment', __name__, url_prefix='/comments')

create_comment_schema = CreateCommentSchema()
fetch_comments_schema = FetchCommentsSchema()


@comment_bp.route('', methods=['POST'])
@token_required(required_user_info=True)
@inject
async def create_comment(user_info: dict,
                          comment_service: CommentServiceInterface = Provide[Container.comment_service]):
    """When user add a comment to a post"""
    try:
        data = await request.get_json()
        data['replied_comment_id'] = data.get('replied_comment_id', None)
        """Validate request data"""
        create_comment_schema.load(data)
        data['user_id'] = user_info['id']

        response = await comment_service.create_comment(data)
        return jsonify(response), 200 if response.get('status') == 0 else 500 if response.get('status') == 1 else 400
    except ValidationError as err:
        return jsonify({"error": "Validation failed",  "status": 1, "messages": err.messages}), 400
    except Exception as err:
        print(err)
        return jsonify({"status": 1, "messages": "There's something wrong"}), 500

@comment_bp.route('/post/<post_id>', methods=['GET'])
@inject
async def fetch_comments(post_id: str, comment_service: CommentServiceInterface = Provide[Container.comment_service]):
    """When user add a comment to a post"""
    try:
        """Validate request data"""
        query_params = fetch_comments_schema.load({**request.args, "post_id": post_id})
        page, size = query_params["page"], query_params["size"]
        response = await comment_service.fetch_comments(post_id, size, page, request.headers)
        return jsonify(response), 200 if response.get('status') == 0 else 500 if response.get('status') == 1 else 400
    except ValidationError as err:
        return jsonify({"error": "Validation failed",  "status": 1, "messages": err.messages}), 400
    except Exception as err:
        print(err)
        return jsonify({"status": 1, "messages": "There's something wrong"}), 500