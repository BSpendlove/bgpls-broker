from app import app
from flask import Blueprint, request
import json

bp = Blueprint("api", __name__, url_prefix="/api/v1")

@bp.route("/test", methods=["GET"])
def test_get():
    return {"test": True}

@bp.route("/test", methods=["POST"])
def test_post():
    if not request.is_json:
        return {"error": True, "message": "Request is not valid."}

    data = request.get_json()
    return {"error": False, "data": data}
