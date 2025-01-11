from quart import Blueprint

app_bp = Blueprint('app', __name__)

@app_bp.route("/")
def hello_world():
    return "<p>Post service api</p>"