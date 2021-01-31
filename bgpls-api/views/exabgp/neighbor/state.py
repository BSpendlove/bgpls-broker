from app import app
from flask import Blueprint, request
import json

bp = Blueprint("state", __name__, url_prefix="/exabgp/neighbor")

@bp.route("/state", methods=["POST"])
def neighbor_state():
    if not request.is_json:
        return {"error": True, "message": "Incorrect format (must be JSON)."}

    data = request.get_json()
    if not data["type"] == "state":
        return {"error": True, "message": "BGP Message has been routed to wrong API endpoint."}

    app.logger.debug("Neighbor State received:\n{}".format(json.dumps(data, indent=4)))
    return {"error": False}