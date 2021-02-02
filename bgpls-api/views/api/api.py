from app import app
from modules.mongodb import MongoDB
from flask import Blueprint, request
import json

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.route("/get_topology/<int:asn>", methods=["GET"])
def mongodb_get_topology_asn(asn):
    mongodb = MongoDB()

    topology = {"nodes":[]}
    nodes = mongodb.find("bgpls_nodes", {"node-descriptors.autonomous-system": asn})
    for node in nodes:
        node_id = node["node_id"]
        node_links = mongodb.find("bgpls_links", {"node_id": node_id})
        node_prefixes_v4 = mongodb.find("bgpls_prefixes_v4", {"node_id": node_id})
        node_prefixes_v6 = mongodb.find("bgpls_prefixes_v6", {"node_id": node_id})

        node.update({
            "asn": asn,
            "links": node_links,
            "prefixes-v4": node_prefixes_v4,
            "prefixes-v6": node_prefixes_v6
        })
        topology["nodes"].append(node)
    return {"error": False, "data": topology}