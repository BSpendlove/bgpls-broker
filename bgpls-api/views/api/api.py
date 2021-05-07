from app import app
from modules.mongodb import MongoDB
from flask import Blueprint
import json

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.route("/get_topology/<int:asn>", methods=["GET"])
def mongodb_get_topology_asn(asn):
    mongodb = MongoDB()

    topology = {"nodes":[]}
    nodes = mongodb.find("bgpls_nodes", {"node-descriptors.autonomous-system": asn})
    for node in nodes:
        node_id = node["node-id"]
        node_links = mongodb.find("bgpls_links", {"node-id": node_id})
        node_prefixes_v4 = mongodb.find("bgpls_prefixes_v4", {"node-id": node_id})
        node_prefixes_v6 = mongodb.find("bgpls_prefixes_v6", {"node-id": node_id})

        node.update({
            "asn": asn,
            "links": node_links,
            "prefixes-v4": node_prefixes_v4,
            "prefixes-v6": node_prefixes_v6
        })
        topology["nodes"].append(node)
    mongodb.close()
    return {"error": False, "data": topology}