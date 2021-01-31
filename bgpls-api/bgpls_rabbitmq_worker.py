from app import app
from os import environ
from modules.exabgp_message_handler import exabgp_generic_handler 
import multiprocessing
import pika
import os

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='rabbitmq',
        credentials=pika.PlainCredentials(environ.get("RABBITMQ_USERNAME"), environ.get("RABBITMQ_PASSWORD"))))
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)

    def callback(ch, method, properties, body):
        bgp_update = body.decode()
        p = multiprocessing.Process(target=exabgp_generic_handler, args=(bgp_update,))
        p.start()

    channel.basic_consume(queue="task_queue",
            auto_ack=True,
            on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
