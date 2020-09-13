import json
from config import ConfigProcessor
from cv_processor import CvProcessor
from amqp_processor import AmqpProcessor
from pgdb import PostgreSqlDatabase
import requests
from upload import upload_one_image


def create_callback(amqp_processor: AmqpProcessor, cv_processor: CvProcessor,
                    pg_db: PostgreSqlDatabase):

    # we use function closure style, because you might want to send additional variables to callback

    def callback(channel, method, properties, body):
        # 1.
        in_msg_dict = json.loads(body.decode())
        print('msg_dict =', in_msg_dict)

        img_link = in_msg_dict['Link']

        # 2.
        local_file_path = img_link.split('/')[-1]
        with open(local_file_path, 'wb') as handle:
            response = requests.get(img_link, stream=True)

            if not response.ok:
                print('NOT RESPONSE OK!')
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)


        # 3. CV processing
        res_img_path, result = cv_processor.inference(local_file_path)
        res_link = upload_one_image(res_img_path)
        print('uploaded result link=', res_link)
        result['task_id'] = in_msg_dict['TaskId']
        result['result_link'] = res_link

        # 4.
        pg_db.write_cv_result(result)
        pg_db.connection.commit()

        # 5.
        out_msg = json.dumps(result)
        print('out_msg:', out_msg)
        amqp_processor.send_message(out_msg)

        # 6. Deliver message ack
        channel.basic_ack(delivery_tag=method.delivery_tag)

    return callback


if __name__ == '__main__':
    print('START')
    json_path = './config/prod.json' # or read from command line

    # 1.
    config_processor = ConfigProcessor(json_path)
    cfg = config_processor.get_configs()
    print(cfg)

    # 2. RabbitMq
    amqp_processor = AmqpProcessor(cfg['rabbit_mq'])

    # 3. Database
    pg_db = PostgreSqlDatabase(cfg)

    # 4.
    cv_processor = CvProcessor()

    # 5. Start to listen incoming messages
    try:
        channel = amqp_processor.establish_connection(create_callback(amqp_processor, cv_processor, pg_db))
        channel.start_consuming()
    except:
        amqp_processor.close_connection()
        # re-raise the last exception (maybe useful for Docker container!)
        raise

    print('END')