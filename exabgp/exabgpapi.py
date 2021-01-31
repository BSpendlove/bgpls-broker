#!/usr/bin/env python
import logging
import json
import os
import requests
import env_file
from sys import stdin, stdout

logging.basicConfig(level=logging.DEBUG)

def message_parser(line):
    temp_message = None
    try:
        temp_message = json.loads(line)
    except Exception as error:
        logging.debug("Error trying json.loads() on line: \n{}".format(line))
        logging.debug("Exception Error was: {}".format(error))
    return temp_message

api_details = env_file.get(path="/exabgp/env/api")
api_url = api_details["API_URL"]

counter = 0
while True:
    try:
        line = stdin.readline().strip()
        
        if line == "":
            counter += 1
            if counter > 100:
                break
            continue
        counter = 0
        
        message = message_parser(line)
        url = None
        if message:
            logging.debug("Message received from peer...\n{}".format(json.dumps(message)))
            if message["type"] == "state":
                url = "{}/exabgp/neighbor/state".format(api_url)
            #url = "{}/api/v1/test".format(api_url)
            if url:
                requests.post(url, json=message)

    except KeyboardInterrupt:
        pass
    except IOError:
        pass
