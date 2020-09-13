import redis


class RedisDb:
    def __init__(self, redis_connection_cfg, db=0, subscribers_set_name='subscribers'):
        self.subscribers_set_name = subscribers_set_name
        host, port = redis_connection_cfg['host'], redis_connection_cfg['port']
        self.redis = redis.Redis(host=host, port=port, db=db)

    def close_connection(self):
        # https://stackoverflow.com/questions/24875806/redis-in-python-how-do-you-close-the-connection
        pass # NOTHING TO DO

    def insert_subscriber(self, id):
        self.redis.sadd(self.subscribers_set_name, id)

    def remove_subscriber(self, id):
        self.redis.srem(self.subscribers_set_name, id)

    def subscribers_list(self):
        subscribers = self.redis.smembers(self.subscribers_set_name)
        return [int(chat_id) for chat_id in subscribers]
