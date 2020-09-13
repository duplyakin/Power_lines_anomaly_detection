import os, json
from bot import TgBot
from redisdb import RedisDb
from config import ConfigProcessor
from amqp_processor import AmqpProcessor


redis_db = None

def prepare_msg(in_notification_dict):
    task_id = in_notification_dict['task_id']
    line_broken = in_notification_dict['line_broken']
    vibration_damper_displacement = in_notification_dict['vibration_damper_displacement']
    garland_problem = in_notification_dict['garland_problem']
    result_link = in_notification_dict['result_link']
    if line_broken == 0 and vibration_damper_displacement == 0 and garland_problem == 0:
        return None
    msg = "Во время анализа задания (ID = {}) было выявлено:\n".format(task_id)
    if line_broken > 0:
        msg = msg + "* обрыв провода\n"
    if vibration_damper_displacement > 0:
        msg = msg + "* смещение виброгасителя\n"
    if garland_problem > 0:
        msg = msg + "* отсутствие изолятора в гасителе\n"
    msg = msg + "Ссылка на результат: {}".format(result_link)
    return msg


def create_callback(tgbot):

    # we use function closure style, because you might want to send additional variables to callback

    def callback(channel, method, properties, body):
        # 1.
        in_notification_dict = json.loads(body.decode())
        print('in_notification_dict=', in_notification_dict)

        # 2. Send notifications to subscribers
        subscribers = redis_db.subscribers_list()
        msg = prepare_msg(in_notification_dict)
        if msg is not None:
            for chat_id in subscribers:
                tgbot.send_notification(chat_id, msg)

        # 3. Deliver message ack
        channel.basic_ack(delivery_tag=method.delivery_tag)

    return callback


def main():
    # 1. Read configs
    config_processor = ConfigProcessor('../')
    cfg = config_processor.get_configs()
    print("cfg=", cfg)

    # 2. Redis
    global redis_db
    redis_db = RedisDb(cfg['redis'])

    # 3. Telegram Bot updater object
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if BOT_TOKEN is None:
        raise RuntimeError("You have to set BOT_TOKEN environment variable")
    tgbot = TgBot(BOT_TOKEN, redis_db)
    # polling in a separate thread
    tgbot.start_polling()

    # 4. Listen to RabbitMQ
    amqp_processor = AmqpProcessor(cfg['rabbit_mq'])
    channel = amqp_processor.establish_connection(create_callback(tgbot))
    channel.start_consuming()


if __name__ == '__main__':
    main()
