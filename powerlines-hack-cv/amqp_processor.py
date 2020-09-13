import pika


class AmqpProcessor:

    def __init__(self, rabbitmq_cfg):
        self.rabbitmq_config = rabbitmq_cfg
        self.connection = self._get_connection()

        # NOTE: we use only one channel for everything
        # Interesting link: https://stackoverflow.com/questions/18418936/rabbitmq-and-relationship-between-channel-and-connection
        self.channel = self.connection.channel()

    def _get_connection(self, heartbeat=0):
        user = self.rabbitmq_config["user"]
        host = self.rabbitmq_config["host"]
        port = self.rabbitmq_config["port"]
        password = self.rabbitmq_config["password"]
        credentials = pika.PlainCredentials(user, password)

        # Maybe you want to set 'heartbeat' parameter to 0 (== disable heartbeat)
        # The default heartbeat=None to accept broker's value, which is usually 60 seconds.

        # UPD: disable heartbeat (default value of heartbeat parameter == 0)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, heartbeat=heartbeat, port=port, credentials=credentials)
        )
        return connection

    def establish_connection(self, callback):
        """
        WARNING: this function doesn't create any entity (exchange, queue, etc.) in the RabbitMQ.
        Thus, you have to prepare RabbitMQ entities before using this module.
        :param callback: callback function
        :return: channel
        """
        channel = self.channel
        queue = self.rabbitmq_config["listen_queue"]
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue, on_message_callback=callback)
        return channel

    def close_connection(self):
        self.connection.close()

    def send_message(self, message):
        to_exchange = self.rabbitmq_config["to_exchange"]

        # WARNING: we use an exchange of fanout type to NOTIFICATION API queues,
        # so it ignores routing key values, but RabbitMQ API needs this value.
        # Thus, we set it to empty string.
        routing_key = ""

        self.channel.basic_publish(exchange=to_exchange,
                                   routing_key=routing_key,
                                   body=message,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                   )
                                   )
