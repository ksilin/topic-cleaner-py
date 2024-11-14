import argparse
import logging
from confluent_kafka.admin import AdminClient, NewTopic


def parse_properties(properties_file):
    properties = {}
    with open(properties_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split('=', 1)
                properties[key.strip()] = value.strip()
    return properties


def create_topic(broker, topic_name, partitions, topic_properties_file):
    try:
        admin_client = AdminClient({'bootstrap.servers': broker})
        topic_config = parse_properties(topic_properties_file) if topic_properties_file else {}

        topic = NewTopic(
            topic=topic_name,
            num_partitions=partitions,
            replication_factor=1,  # Set replication factor to 1 for local - CHANGE THIS FOR CCLOUD
            config=topic_config
        )
        futures = admin_client.create_topics([topic])

        for topic, future in futures.items():
            try:
                future.result()
                logging.info(f"Topic '{topic_name}' successfully created on broker '{broker}'.")
            except Exception as e:
                logging.error(f"Failed to create topic '{topic_name}': {e}")
    except Exception as e:
        logging.error(f"Error while creating topic: {e}")


def main():
    parser = argparse.ArgumentParser(description="Kafka Topic Creator")
    parser.add_argument("-b", "--broker-config", help="Path to the broker properties file")
    parser.add_argument("-t", "--topic-name", type=str, required=True, help="Name of the topic to create")
    parser.add_argument("-p", "--partitions", type=int, required=True, help="Number of partitions for the topic")
    parser.add_argument("-c", "--topic-config", help="Path to the topic properties file")

    args = parser.parse_args()

    broker = "localhost:29092"
    if args.broker_config:
        broker_properties = parse_properties(args.broker_config)
        broker = broker_properties.get("bootstrap.servers", broker)

    create_topic(broker, args.topic_name, args.partitions, args.topic_config)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
