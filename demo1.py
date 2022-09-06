import time
import json

import pika

USERNAME = 'mqtt'
PASSWORD = 'mqtt'

credentials = pika.PlainCredentials(USERNAME, PASSWORD)
connection = pika.BlockingConnection(pika.ConnectionParameters(host='47.97.183.24', port=5672, credentials=credentials))
channel = connection.channel()
# channel.queue_declare(queue='test.fanout.queue')
count = 0
data = {
    "deep": 12,
    "deviceId": "XXLJC4LCGSCSD1DA007",
    "mapId": 1539911190092759042,
    "jwd": [114.321321, 31.312231],
    "gjwd": [114.121321, 31.112231]
}
while True:
    # channel.basic_publish(exchange='fanout_test_exchange', routing_key='test', body='1')
    print(time.time(), count)
    data.update({'deep': count})
    channel.basic_publish(exchange='fanout_test_exchange', routing_key='test', body=json.dumps(data))
    # channel.basic_publish(exchange='fanout_test_exchange', routing_key='test', body='3')
    count += 1
    if count > 4999:
        break
    time.sleep(0.3)
print('send success msg to rabbitmq')
connection.close()  # 关闭连接
