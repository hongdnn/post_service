from quart_cors import cors
from quart import Quart
from src.infrastructure.config import Config
from src.infrastructure.database import init_db
from src.infrastructure.dependency_container import Container
from src.presentation import blueprints


def create_app():
    app = Quart(__name__)
    app = cors(app,
               allow_origin=[Config.CHAT_SERVICE_BASE_URL, Config.FRONTEND_BASE_URL],
               allow_methods=["GET", "POST", "OPTIONS"],
               allow_headers=["Authorization", "Content-Type"],
               allow_credentials=True)
    app.config.from_object(Config)
    container = Container()
    container.wire(
        modules=[
            'src.presentation.routes.post_route',
            'src.presentation.routes.reaction_route'
        ]
    )
    # Run the async database initialization
    init_db(app, container)
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    return app