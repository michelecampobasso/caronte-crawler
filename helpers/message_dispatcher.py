import pika

from utils.commons import print_internals


class MessageDispatcher:

    def __init__(self):
        pass

    """
    This function establishes a connection against a local MQTT server, binds to test channel and sets its communication
    to publish.
    
    @param data: data to be sent as a Json.
    """
    def send_one_json(self, data):

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='test')
        channel.basic_publish(exchange='',
                              routing_key='test',
                              body=data)
        print_internals("[TRAINER - LISTENER] Sent " + str(data))
        connection.close()

    """
    This function establishes a connection against a local MQTT server, binds to test channel and sets its communication
    to receive.
    
    @param callback: is a function that specifies the behavior on data receive.
    """
    def receive_one_json(self, callback):

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='test')
        channel.basic_consume(callback,
                              queue='test',
                              no_ack=True)
        channel.start_consuming()
