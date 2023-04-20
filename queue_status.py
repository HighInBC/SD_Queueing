#!/usr/bin/env python3
import json
import sys

import redis_handler

def load_config(config_file="config.json"):
    with open(config_file, "r") as f:
        config = json.load(f)
    return config

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
    config = load_config()
    try:
        redis_connection = redis_handler.connect_to_redis(config)
    except redis_handler.InvalidInputException as e:
        print(f"Error: {e}")
        sys.exit(1)

    ingress_queue = config.get("ingress_queue", "default_ingress_queue")
    return_queue = config.get("return_queue", "default_return_queue")

    queue_info = get_queue_info(redis_connection, ingress_queue, return_queue)

    print("Queue status:")
    print(json.dumps(queue_info, indent=2))

if __name__ == "__main__":
    main()
