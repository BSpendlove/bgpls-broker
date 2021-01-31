import json

def parse_neighbor_state(message):
    """Prepares a dict from a raw BGP State Message to be used in the database"""
    parsed_message =  {
        "exabgp_version": message["exabgp"],
        "time": message["time"],
        "host": message["host"],
        "pid": message["pid"],
        "ppid": message["ppid"],
        "counter": message["counter"],
        "local_address": message["neighbor"]["address"]["local"],
        "peer_address": message["neighbor"]["address"]["peer"],
        "local_asn": message["neighbor"]["asn"]["local"],
        "peer_asn": message["neighbor"]["asn"]["peer"],
        "state_type": message["neighbor"]["state"]
    }

    if message["neighbor"]["state"] == "down":
        parsed_message["state_reason"] = message["neighbor"]["reason"]

    return parsed_message