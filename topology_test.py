import requests
import json
import sys
from terminaltables import AsciiTable

req = requests.request(
    "GET",
    "http://10.4.20.129:5000/api/get_topology/65510"
)

topology = json.loads(req.text)
if topology["error"]:
    print(topology["message"])
    sys.exit()

table_data = [["Node", "Link", "Neighbor", "TE Metric", "IGP Metric", "Unreserved BW", "Adj SIDS", "Node Pfxs", "Node Pfx SIDs"]]

for node in topology["data"]["nodes"]:
    node_name = node["attributes"]["bgp-ls"]["node-name"]
    links = []
    for link in node["links"]:
        links.append(
            [
                node_name,
                link["interface-address"]["interface-address"],
                link["neighbor-address"]["neighbor-address"],
                link["attributes"]["bgp-ls"]["te-metric"] if "te-metric" in link["attributes"]["bgp-ls"] else None,
                link["attributes"]["bgp-ls"]["igp-metric"],
                str(link["attributes"]["bgp-ls"]["unreserved-bandwidth"]) if "unreserved-bandwidth" in link["attributes"]["bgp-ls"] else None,
                str(link["attributes"]["bgp-ls"]["sids"]) if "sids" in link["attributes"]["bgp-ls"] else None
            ]
        )
    #print(node_name)
    node_prefixes = []
    for prefix in node["prefixes-v4"]:
        prefix_flags = prefix["attributes"]["bgp-ls"]["sr-prefix-attribute-flags"]
        for flag in prefix_flags:
            if flag.lower() == "n": # N-Flag - https://tools.ietf.org/html/draft-ietf-isis-segment-routing-extensions-15#section-2.1.1
                if prefix_flags[flag] == 1:
                    node_prefixes.append(prefix)
    #print(node_prefixes)
    table_data += links
    table_data += [[
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "\n".join([p["ip-reach-prefix"] for p in node_prefixes]),
        "\n".join([str(p["attributes"]["bgp-ls"]["sids"]) for p in node_prefixes])
    ]]

table = AsciiTable(table_data)
print(table.table)