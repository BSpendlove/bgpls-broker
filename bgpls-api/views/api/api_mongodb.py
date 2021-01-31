from app import app
from modules.mongodb import MongoDB
from flask import Blueprint, request
import json

bp = Blueprint("api_mongodb", __name__, url_prefix="/api/mongodb")

@bp.route("/get_collections", methods=["GET"])
def mongodb_get_collections():
    mongodb = MongoDB()

    return {"error": False, "data": mongodb.get_collections()}

@bp.route("/delete_collection/<string:collection>", methods=["DELETE"])
def mongodb_delete_collection(collection):
    mongodb = MongoDB()

    return {"error": False, "data": str(mongodb.delete_collection(collection))}

@bp.route("/neighbor_state", methods=["GET"])
def mongodb_get_neighbor_state():
    mongodb = MongoDB()

    return {"error": False, "data": mongodb.find("neighbor_state")}
