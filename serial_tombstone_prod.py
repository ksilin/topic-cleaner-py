import argparse
import time
import sys
import json
from confluent_kafka import Producer, KafkaException

def produce_messages(producer, topic_name, keys, num_messages, wait_time):
    for key in keys:
        for i in range(num_messages):
            value = json.dumps({'key': key, 'value': f'message_{i}'})
            try:
                producer.produce(topic_name, key=key, value=value, callback=delivery_report)
                print(f"Producing message to topic '{topic_name}': key='{key}', value='message_{i}'")
            except KafkaException as e:
                print(f"Failed to produce message: {str(e)}")
            producer.poll(0)
            time.sleep(wait_time / 1000.0)
        try:
            producer.produce(topic_name, key=key, value=None, callback=delivery_report)
            print(f"Producing tombstone for key '{key}' in topic '{topic_name}'")
        except KafkaException as e:
            print(f"Failed to produce tombstone: {str(e)}")
        producer.poll(0)
    producer.flush()

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CLI Producer Script')
    parser.add_argument('--topic', type=str, required=True, help='The topic name to produce to')
    parser.add_argument('--keys', type=str, required=True, help='Comma-separated list of string keys')
    parser.add_argument('--num_messages', type=int, required=True, help='Number of messages to produce per key')
    parser.add_argument('--wait_time', type=int, required=True, help='Time in milliseconds to wait between each message')
    parser.add_argument('--properties', type=str, required=False, default='localhost:29092', help='Kafka broker properties file or broker address (default: localhost:9092)')

    args = parser.parse_args()

    topic_name = args.topic
    keys = args.keys.split(',')
    num_messages = args.num_messages
    wait_time = args.wait_time
    kafka_broker = args.properties

    if num_messages < 0:
        sys.exit("Error: num_messages should be greater than or equal to 0.")
    if wait_time < 0:
        sys.exit("Error: wait_time should be greater than or equal to 0.")

    conf = {'bootstrap.servers': kafka_broker}
    try:
        producer = Producer(conf)
    except KafkaException as e:
        sys.exit(f"Error: Failed to create Kafka producer - {str(e)}")

    produce_messages(producer, topic_name, keys, num_messages, wait_time)
