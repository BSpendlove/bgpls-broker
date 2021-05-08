from app import app
from flask import Blueprint, request
from modules.rabbitmq import Publisher
from os import environ
import json
import pika

bp = Blueprint("exabgp", __name__, url_prefix="/exabgp")

@bp.route("/", methods=["POST"])
def exabgp():
    if not request.is_json:
        return {"error": True, "message": "Incorrect format (must be JSON)."}

    data = request.get_json()
    if not data:
        return {"error": True, "message": "No JSON data found."}
    
    try:
        publisher = Publisher(config={
            "host": "rabbitmq",
            "username": environ.get("RABBITMQ_USERNAME"),
            "password": environ.get("RABBITMQ_PASSWORD")
        })

        publisher.connect()
        publisher.publish(data)
        publisher.close()
    except Exception as error:
        app.logger.debug("Error connecting to rabbitmq.\nReason: {}".format(error))
    return {"error": False}
