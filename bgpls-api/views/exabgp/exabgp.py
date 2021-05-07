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
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='rabbitmq',
            credentials=pika.PlainCredentials(environ.get("RABBITMQ_USERNAME"), environ.get("RABBITMQ_PASSWORD"))))
        channel = connection.channel()
        channel.queue_declare(queue='task_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
        ))
        connection.close()
        """
    except Exception as error:
        app.logger.debug("Error connecting to rabbitmq.\nReason: {}".format(error))
    return {"error": False}
