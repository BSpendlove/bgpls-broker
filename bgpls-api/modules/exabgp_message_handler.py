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
    #       announce
    #         bgp-ls
    #           bgpls-node
    #           bgpls-link
    #           bgpls-prefix-v4
    #           bgpls-prefix-v6

    bgp_message = json.loads(change_keys(bgp_message, convert))
    app.logger.debug("bgp_message after normalizing keys:\n{}".format(bgp_message))
    if bgp_message["type"] == "state":
        exabgp_state(bgp_message)

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

    state = bgp_message["neighbor"]["state"]
    return states[state](bgp_message)

def exabgp_state_connected(bgp_message):
    peer = bgp_message["neighbor"]["address"]["peer"]

    mongodb = MongoDB()
    find_peer = mongodb.find_one("neighbor_state", {"neighbor.address.peer": peer}, {"_id": False})
    if not find_peer:
        # Create neighbor_state
        result = mongodb.insert_one("neighbor_state", bgp_message)
        app.logger.debug("neighbor_state CONNECTED for neighbor {} doesn't exist. Result: {}".format(peer, result))
        return result
    app.logger.debug("neighbor_state CONNECTED for neighbor {} exist. Updating existing entry {}".format(peer, json.dumps(find_peer, indent=4)))
    return find_peer

def exabgp_state_up(bgp_message):
    app.logger.debug("Detected up state message")

def exabgp_state_down(bgp_message):
    app.logger.debug("Detected down state message")

def change_keys(obj, convert):
    """
    Recursively goes through the dictionary obj and replaces keys with the convert function.
    https://stackoverflow.com/questions/11700705/python-recursively-replace-character-in-keys-of-nested-dictionary/38269945 by baldr
    """
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for k, v in obj.items():
            new[convert(k)] = change_keys(v, convert)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(change_keys(v, convert) for v in obj)
    else:
        return obj
    return new

def convert(k):
    return k.replace('.', '_')
