from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

def init_db(app, container):
    """Initialize the database for migration"""
    Migrate(app, db)

    @app.before_serving
    async def before_serving():
        await check_db_connection(container)


async def check_db_connection(container):
    """Check if the database connection is successful."""
    engine = container.engine()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")