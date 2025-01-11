import uvicorn
from src import create_app

app = create_app()

if __name__ == '__main__':

    uvicorn.run(app, port=5001, log_level="debug")

