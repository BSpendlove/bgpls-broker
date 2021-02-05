import requests
import json
import sys

req = requests.request(
    "GET",
    "http://10.4.20.129:5000/api/get_topology/65510"
)

topology = json.loads(req.text)
if topology["error"]:
    print(topology["message"])
    sys.exit()

for node in topology["data"]["nodes"]:
    node_name = node["attributes"]["bgp-ls"]["node-name"]
    print(node_name)
    for link in node["links"]:
        print("Link: {}".format(link["interface-address"]["interface-address"]))
        print("TE Metric: {}".format(link["attributes"]["bgp-ls"]["te-metric"]))
        print("IGP Metric: {}".format(link["attributes"]["bgp-ls"]["igp-metric"]))
        print("Unreserved Bandwidth: {}".format(link["attributes"]["bgp-ls"]["unreserved-bandwidth"]))
        print("SR SIDs: {}".format(link["attributes"]["bgp-ls"]["sids"]))
        print("\n")