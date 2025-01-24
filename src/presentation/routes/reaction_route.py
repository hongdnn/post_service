from dependency_injector.wiring import Provide, inject
from marshmallow import ValidationError
from quart import Blueprint, request, jsonify

from src import Container
from src.domain.services.reaction_service import ReactionService, ReactionServiceInterface
from src.infrastructure.jwt_handler import token_required
from src.presentation.schemas.reaction_schema import UpdateReactionSchema

reaction_bp = Blueprint('reaction', __name__, url_prefix='/reactions')

update_reaction_schema = UpdateReactionSchema()

@reaction_bp.route('', methods=['POST'])
@token_required(required_user_info=True)
@inject
async def update_reaction(user_info: dict, reaction_service: ReactionServiceInterface = Provide[Container.reaction_service]):
    """Update user reaction in a post."""
    try:
        data = await request.get_json()
        """Validate request data"""
        update_reaction_schema.load(data)
        data['user_id'] = user_info['id']

        response = await reaction_service.update_reaction(data)
        return jsonify(response), 200 if response.get('status') == 0 else 500 if response.get('status') == 1 else 400
    except ValidationError as err:
        return jsonify({"error": "Validation failed",  "status": 1, "messages": err.messages}), 400
    except Exception as err:
        print(err)
        return jsonify({"status": 1, "messages": "There's something wrong"}), 500