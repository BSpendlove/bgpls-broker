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

    neighbors = mongodb.find("neighbor_state")
    return {"error": False, "data": neighbors, "count": len(neighbors)}

@bp.route("/bgpls_nodes", methods=["GET"])
def mongodb_get_bgpls_nodes():
    mongodb = MongoDB()

    nodes = mongodb.find("bgpls_nodes")
    return {"error": False, "data": nodes, "count": len(nodes)}

@bp.route("/bgpls_links", methods=["GET"])
def mongodb_get_bgpls_links():
    mongodb = MongoDB()

    links = mongodb.find("bgpls_links")
    return {"error": False, "data": links, "count": len(links)}

@bp.route("/bgpls_prefixes_v4", methods=["GET"])
def mongodb_get_bgpls_prefixes_v4():
    mongodb = MongoDB()

    prefixes_v4 = mongodb.find("bgpls_prefixes_v4")
    return {"error": False, "data": prefixes_v4, "count": len(prefixes_v4)}
