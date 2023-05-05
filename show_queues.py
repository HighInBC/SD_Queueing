#!/usr/bin/env python3
import sys
import json

from sdq.redis_handler import connect_to_redis, InvalidInputException
from sdq.config_parser import ConfigParser  # Import the ConfigParser class

def get_queue_info(redis_connection, ingress_queue, return_queue):
    info = {}
    info['ingress_queue'] = {}
    for i in range(6):
        queue_name = f"{ingress_queue}_priority_{i}"
        info['ingress_queue'][queue_name] = redis_connection.llen(queue_name)

    info['return_queue'] = {}
    info['return_queue']['length'] = redis_connection.llen(return_queue)

    return info

def main():
    # Create an instance of the ConfigParser class
    config_parser = ConfigParser(config_file='config.json')

    try:
        redis_connection = connect_to_redis(config_parser)
    except InvalidInputException as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Access the values using the properties of the ConfigParser class
    ingress_queue = config_parser.ingress_queue
    return_queue = config_parser.return_queue

    queue_info = get_queue_info(redis_connection, ingress_queue, return_queue)

    print("Queue status:")
    print(json.dumps(queue_info, indent=2))

if __name__ == "__main__":
    main()
