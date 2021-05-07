from app import app
from collections.abc import Mapping
from modules.mongodb import MongoDB
import json

def exabgp_generic_handler(bgp_message):
    # Types of messages:
    #   state
    #     connected
    #     up
    #     down
    #   update
    #     receive
    #       attribute
    #       announce
    #         bgp-ls
    #           bgpls-node
    #           bgpls-link
    #           bgpls-prefix-v4
    #           bgpls-prefix-v6

    bgp_message = json.loads(normalize_keys(bgp_message, convert)) # Ensures any dict keys replace . with _ (eg. IP addresses)
    app.logger.debug("bgp_message received, type is:\n{}".format(bgp_message["type"]))
    app.logger.debug("========= Message ========\n{}".format(json.dumps(bgp_message, indent=4)))
    if bgp_message["type"] == "state":
        exabgp_state(bgp_message)
    if bgp_message["type"] == "update":
        if "eor" in bgp_message["neighbor"]["message"]: # End of RIB
            app.logger.debug("---- Received EOR message -----")
            return None
        if "withdraw" in bgp_message["neighbor"]["message"]["update"]:
            app.logger.debug("---- Received WITHDRAW message -----")
            withdraw_bgpls_updates(bgp_message)
        else:
            exabgp_update(bgp_message)

def exabgp_state(bgp_message):
    # When a state messages arrives, the worker will maintain a state of the relevant database collections
    # that may require some attention. For example, if we receive a down or connected state
    # while the current neighbor_state for Peer X is in a stable state "up". We need to flush/withdraw
    # all BGP updates received from this neighbor (since either the BGP session has flapped, or the application
    # has restarted...
    # Keepalives should update the existing neighbor state if it is stable ("connected") otherwise all
    # bgpls_nodes, bgpls_links, bgpls_prefixes_v4, and bgpls_prefixes_v6 related to that specific neighbor
    # should be flushed from the database.
    states = {
        "connected": exabgp_state_connected,
        "up": exabgp_state_up,
        "down": exabgp_state_down
    }

    state_type = bgp_message["neighbor"]["state"]
    return states[state_type](bgp_message)

def exabgp_state_connected(bgp_message):
    # Inserts/Updates a state in the neighbor_state collection
    asn = bgp_message["neighbor"]["asn"]["peer"]
    peer = bgp_message["neighbor"]["address"]["peer"]
    mongodb = MongoDB()
    update_peer = mongodb.update("neighbor_state", {"neighbor.address.peer": peer}, bgp_message)
    mongodb.close()
    app.logger.debug("Inserted/Updated BGP Neighbor ({}) results: {}".format(peer, update_peer))
    return update_peer

def exabgp_state_up(bgp_message):
    asn = bgp_message["neighbor"]["asn"]["peer"]
    peer = bgp_message["neighbor"]["address"]["peer"]
    withdraw_neighbor_updates(asn, peer) # Flush any BGP-LS Updates learned via the ExaBGP neighbor
    mongodb = MongoDB()
    update_peer = mongodb.update("neighbor_state", {"neighbor.address.peer": peer}, bgp_message)
    mongodb.close()
    app.logger.debug("Inserted/Updated BGP Neighbor ({}) results: {}".format(peer, update_peer))
    return update_peer

def exabgp_state_down(bgp_message):
    asn = bgp_message["neighbor"]["asn"]["peer"]
    peer = bgp_message["neighbor"]["address"]["peer"]
    withdraw_neighbor_updates(asn, peer) # Flush any BGP-LS Updates learned via the ExaBGP neighbor
    bgp_message.update({
        "last_down": bgp_message["time"],
        "last_down_reason": bgp_message["neighbor"]["reason"]
    })
    del bgp_message["neighbor"]["reason"]
    mongodb = MongoDB()
    update_peer = mongodb.update("neighbor_state", {"neighbor.address.peer": peer}, bgp_message)
    mongodb.close()
    app.logger.debug("Inserted/Updated BGP Neighbor ({}) results: {}".format(peer, update_peer))
    return update_peer

def exabgp_update(bgp_message):
    updates = {
        "bgpls-node": exabgp_update_node,
        "bgpls-link": exabgp_update_link,
        "bgpls-prefix-v4": exabgp_update_prefix_v4,
        "bgpls-prefix-v6": exabgp_update_prefix_v6
    }
    # All updates should be handled by 1 generic function or separate?
    for update_type in updates:
        if update_type in str(bgp_message):
            return updates[update_type](bgp_message)

def exabgp_update_node(bgp_message):
    # Inesrts/Updates a BGPLS Node entry
    asn = bgp_message["neighbor"]["asn"]["peer"]
    peer = bgp_message["neighbor"]["address"]["peer"]
    mongodb = MongoDB()
    nodes = bgp_message["neighbor"]["message"]["update"]["announce"]["bgp-ls bgp-ls"][peer]
    attributes = bgp_message["neighbor"]["message"]["update"]["attribute"]
    updated_nodes = []
    for node in nodes:
        node_id = find_unique_node_id(node)
        node.update({
            "node-id": node_id,
            "attributes": attributes,
            "neighbor": {
                "address": {
                    "peer": peer
                },
                "asn": {
                    "peer": asn
                }
            }
        })
        update_node = mongodb.update("bgpls_nodes", {
            "node-id": node["node-id"],
            "node-descriptors.autonomous-system":  node["node-descriptors"]["autonomous-system"],
            "node-descriptors.router-id": node["node-descriptors"]["router-id"]
        }, node)
        updated_nodes.append(update_node)
    mongodb.close()
    app.logger.debug("Updated bgpls_nodes: {}".format(updated_nodes))
    return updated_nodes

def exabgp_update_link(bgp_message):
    # Inserts/Updates a BGPLS Link entry
    asn = bgp_message["neighbor"]["asn"]["peer"]
    peer = bgp_message["neighbor"]["address"]["peer"]
    mongodb = MongoDB()
    links = bgp_message["neighbor"]["message"]["update"]["announce"]["bgp-ls bgp-ls"][peer]
    attributes = bgp_message["neighbor"]["message"]["update"]["attribute"]
    updated_links = []
    for link in links:
        node_id = find_unique_node_id(link)
        link.update({
            "node-id": node_id,
            "attributes": attributes,
            "neighbor": {
                "address": {
                    "peer": peer
                },
                "asn": {
                    "peer": asn
                }
            }
        })
        update_link = mongodb.update("bgpls_links", {
            "node-id": link["node-id"],
            "local-node-descriptors.autonomous-system":  link["local-node-descriptors"]["autonomous-system"],
            "local-node-descriptors.router-id": link["local-node-descriptors"]["router-id"],
            "interface-address.interface-address": link["interface-address"]["interface-address"]
        }, link)
        updated_links.append(update_link)
    mongodb.close()
    app.logger.debug("Updated bgpls_links: {}".format(updated_links))
    return updated_links

def exabgp_update_prefix_v4(bgp_message):
    # Inesrts/Updates a BGPLS Prefix V4 entry
    asn = bgp_message["neighbor"]["asn"]["peer"]
    peer = bgp_message["neighbor"]["address"]["peer"]
    mongodb = MongoDB()
    prefixes = bgp_message["neighbor"]["message"]["update"]["announce"]["bgp-ls bgp-ls"][peer]
    attributes = bgp_message["neighbor"]["message"]["update"]["attribute"]
    updated_prefixes = []
    for prefix in prefixes:
        node_id = find_unique_node_id(prefix)
        prefix.update({
            "node-id": node_id,
            "attributes": attributes,
            "neighbor": {
                "address": {
                    "peer": peer
                },
                "asn": {
                    "peer": asn
                }
            }
        })
        update_prefix = mongodb.update("bgpls_prefixes_v4", {
                "node-id": prefix["node-id"],
                "node-descriptors.autonomous-system":  prefix["node-descriptors"]["autonomous-system"],
                "node-descriptors.router-id": prefix["node-descriptors"]["router-id"],
                "ip-reachability-tlv": prefix["ip-reachability-tlv"],
                "ip-reach-prefix": prefix["ip-reach-prefix"]
        }, prefix)
        updated_prefixes.append(update_prefix)
    mongodb.close()
    app.logger.debug("Updated bgpls_prefixes_v4: {}".format(updated_prefixes))
    return updated_prefixes

def exabgp_update_prefix_v6(bgp_message):
    # Need to implement
    return

def withdraw_neighbor_updates(asn, address):
    # Will withdraw all related neighbor updates (used when a peer with ExaBGP goes down)
    collections = ["bgpls_nodes", "bgpls_links", "bgpls_prefixes_v4", "bgpls_prefixes_v6"]
    mongodb = MongoDB()
    results = mongodb.remove_from_collections(collections, {"neighbor.asn.peer": asn, "neighbor.address.peer": address})
    mongodb.close()
    app.logger.debug("Withdrawn all updates from {} (ASN: {}) from collections {}.\nResults: {}".format(address, asn, collections, results))
    return results

def withdraw_bgpls_updates(bgp_message):
    # Withdraws updates based on the nlri_type
    asn = bgp_message["neighbor"]["asn"]["peer"]
    peer = bgp_message["neighbor"]["address"]["peer"]
    mongodb = MongoDB()
    nlris = bgp_message["neighbor"]["message"]["update"]["withdraw"]["bgp-ls bgp-ls"]
    results = []
    for nlri in nlris:
        node_id = find_unique_node_id(nlri)
        if nlri["ls-nlri-type"] == "bgpls-node":
            collection = "bgpls_nodes"
            result = mongodb.remove(collection, {
                "node-id": node_id
            })
            app.logger.debug("Withdraw for bgpls-node: {} (results: {})".format(node_id, result))
            results.append(result)
        if nlri["ls-nlri-type"] == "bgpls-link":
            collection = "bgpls_links"
            result = mongodb.remove(collection, {
                "node-id": node_id,
                "l3-routing-topology": nlri["l3-routing-topology"],
                "local-node-descriptors.router-id": nlri["local-node-descriptors"]["router-id"],
                "interface-address.interface-address": nlri["interface-address"]["interface-address"]
            })
            app.logger.debug("Withdraw for bgpls-link: {} (results: {})".format(node_id, result))
            results.append(result)
        if nlri["ls-nlri-type"] == "bgpls-prefix-v4":
            collection = "bgpls_prefixes_v4"
            result = mongodb.remove(collection, {
                "node-id": node_id,
                "l3-routing-topology": nlri["l3-routing-topology"],
                "ip-reachability-tlv": nlri["ip-reachability-tlv"],
                "ip-reach-prefix": nlri["ip-reach-prefix"]
            })
            app.logger.debug("Withdraw for bgpls-prefix-v4: {} (results: {})".format(node_id, result))
            results.append(result)
        if nlri["ls-nlri-type"] == "bgpls-prefix-v6":
            collection = "bgpls_prefixes_v6"
            # Need to implement
    mongodb.close()

def find_unique_node_id(nlri):
    # https://tools.ietf.org/html/draft-ietf-idr-bgpls-segment-routing-epe-19
    # Section 3.2.  Mandatory BGP Node Descriptors
    #  Note that [RFC6286] (section 2.1) requires the BGP identifier
    # (Router-ID) to be unique within an Autonomous System and non-zero.
    # Therefore, the <ASN, BGP Router-ID> tuple is globally unique.
    # node_id is used as a relation between bgpls_node, bgpls_link and bgpls_prefix_v4/v6 in the database.
    # Represented as: ASN:Router-ID (eg. 65510:000000000001)
    common_nlri_types = ["bgpls-node", "bgpls-prefix-v4", "bgpls-prefix-v6"]
    if nlri["ls-nlri-type"] in common_nlri_types:
        node_id = "{}:{}".format(
            nlri["node-descriptors"]["autonomous-system"],
            nlri["node-descriptors"]["router-id"],
        )
        return node_id
    if nlri["ls-nlri-type"] == "bgpls-link":
        node_id = "{}:{}".format(
            nlri["local-node-descriptors"]["autonomous-system"],
            nlri["local-node-descriptors"]["router-id"],
        )
        return node_id

def normalize_keys(obj, convert):
    # Recursively goes through the dictionary obj and replaces keys with the convert function.
    # https://stackoverflow.com/questions/11700705/python-recursively-replace-character-in-keys-of-nested-dictionary/38269945 by baldr
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for k, v in obj.items():
            new[convert(k)] = normalize_keys(v, convert)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(normalize_keys(v, convert) for v in obj)
    else:
        return obj
    return new

def convert(k):
    return k.replace('.', '_')