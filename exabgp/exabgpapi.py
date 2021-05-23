#!/usr/bin/env python
import logging
import json
import os
from modules.rabbitmq import Publisher
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

api_url = os.environ.get("API_URL")
publisher = Publisher(config={
    "host": "rabbitmq",
    "username": os.environ.get("RABBITMQ_USERNAME"),
    "password": os.environ.get("RABBITMQ_PASSWORD")
})

# Initial connect (however publisher.publish will try to handle reconnections)
publisher.connect()

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
            # Send all messages to RabbitMQ Exchange (bgplsapi)
            publisher.publish(message)

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt")
        publisher.close()
        pass
    except IOError:
        logging.info("IOError")
        publisher.close()
        pass
