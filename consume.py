import argparse
import configparser
import random
import sys
import time
from confluent_kafka import Consumer, KafkaError
from colorama import Fore, Style
import signal

# KBD Interrupt
def signal_handler(sig, frame):
    print('\nExiting consumer...')
    if 'consumer' in globals() and consumer is not None:
        consumer.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def read_property_file(property_file_path):
    config = configparser.ConfigParser()
    config.read(property_file_path)
    return dict(config['default']) if 'default' in config else {}

def main():
    parser = argparse.ArgumentParser(description='Kafka CLI Consumer')
    parser.add_argument('-p', '--property-file', type=str, default=None,
                        help='Path to property file for broker connections, defaults to localhost:29092')
    parser.add_argument('-t', '--topic', type=str, required=True, help='Topic name to consume from')
    parser.add_argument('-g', '--group', type=str, default=None, help='Optional consumer group name')
    parser.add_argument('-m', '--mode', type=str, choices=['list', 'view'], default='list',
                        help='Mode of operation: "list" or "view" (default: list)')

    parser.add_argument('-s', '--sleep-time', type=float, default=1.0, help='Time in seconds to sleep between updates (default: 1.0)')
    args = parser.parse_args()

    broker = 'localhost:29092'
    if args.property_file:
        properties = read_property_file(args.property_file)
        broker = properties.get('bootstrap.servers', broker)

    group_id = args.group if args.group else f'random_group_{random.randint(1000, 9999)}'
    topic = args.topic

    conf = {
        'bootstrap.servers': broker,
        'group.id': group_id,
        'auto.offset.reset': 'earliest'
    }

    global consumer
    consumer = Consumer(conf)
    consumer.subscribe([topic])

    key_value_store = {}

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Error: {msg.error()}")
                    continue

            key = msg.key().decode('utf-8') if msg.key() else None
            value = msg.value().decode('utf-8') if msg.value() else None

            if key:
                if value is None:
                    key_value_store[key] = 'TOMBSTONE'
                else:
                    if args.mode == 'view':
                        key_value_store[key] = value
                    elif args.mode == 'list':
                        if key not in key_value_store or key_value_store[key] == 'TOMBSTONE':
                            key_value_store[key] = [value]
                        else:
                            key_value_store[key].append(value)

            # Clear screen
            print(chr(27) + "[2J")
            for k, v in key_value_store.items():
                if v == 'TOMBSTONE':
                    print(f"{k}: {Fore.RED}☠ TOMBSTONE ☠{Style.RESET_ALL}")
                else:
                    if args.mode == 'watch':
                        print(f"{k}: {v}")
                    elif args.mode == 'view':
                        print(f"{k}: {v}")

            time.sleep(args.sleep_time)

    finally:
        consumer.close()

if __name__ == '__main__':
    main()
    