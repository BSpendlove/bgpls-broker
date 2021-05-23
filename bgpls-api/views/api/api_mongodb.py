from app import app
from modules.mongodb import MongoDB
from flask import Blueprint, request
import json

bp = Blueprint("api_mongodb", __name__, url_prefix="/api/mongodb")

@bp.route("/get_collections", methods=["GET"])
def mongodb_get_collections():
    mongodb = MongoDB()
    results = mongodb.get_collections()
    mongodb.close()
    return {"error": False, "data": results}

@bp.route("/delete_collection/<string:collection>", methods=["DELETE"])
def mongodb_delete_collection(collection):
    mongodb = MongoDB()
    results = str(mongodb.delete_collection(collection))
    monogodb.close()
    return {"error": False, "data": results}, 200

@bp.route("/neighbor_state", methods=["GET"])
def mongodb_get_neighbor_state():
    mongodb = MongoDB()
    neighbors = mongodb.find("neighbor_state")
    mongodb.close()
    return {"error": False, "data": neighbors, "count": len(neighbors)}, 200

@bp.route("/neighbor_state/<string:neighbor>", methods=["GET"])
def mongodb_get_neighbor_state_query(neighbor):
    mongodb = MongoDB()
    found_neighbor = mongodb.find("neighbor_state", query_filter={"neighbor.address.peer": neighbor})
    mongodb.close()
    return {"error": False, "data": [found_neighbor] if found_neighbor else []}

@bp.route("/bgpls_nodes", methods=["GET"])
def mongodb_get_bgpls_nodes():
    mongodb = MongoDB()
    nodes = mongodb.find("bgpls_nodes")
    mongodb.close()
    return {"error": False, "data": nodes, "count": len(nodes)}, 200

@bp.route("/bgpls_links", methods=["GET"])
def mongodb_get_bgpls_links():
    mongodb = MongoDB()
    links = mongodb.find("bgpls_links")
    mongodb.close()
    return {"error": False, "data": links, "count": len(links)}, 200

@bp.route("/bgpls_prefixes_v4", methods=["GET"])
def mongodb_get_bgpls_prefixes_v4():
    mongodb = MongoDB()
    prefixes_v4 = mongodb.find("bgpls_prefixes_v4")
    mongodb.close()
    return {"error": False, "data": prefixes_v4, "count": len(prefixes_v4)}, 200
