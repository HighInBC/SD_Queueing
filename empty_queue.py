#!/usr/bin/env python3
import sys
import redis
from sdq.redis_handler import connect_to_redis, InvalidInputException
from sdq.config_parser import ConfigParser

def handle_job(job):
    print("Emptying queue...")

def empty_queue(redis_connection, queue, batch_size=1000):
    while True:
        entries = redis_connection.lrange(queue, 0, batch_size - 1)
        if not entries:
            break
        for entry in entries:
            handle_job(entry)
        redis_connection.ltrim(queue, batch_size, -1)

def main():
    config = ConfigParser(config_file='config.json')

    try:
        redis_connection = connect_to_redis(config)
    except InvalidInputException as e:
        print(f"Error: {e}")
        sys.exit(1)

    queue = sys.argv[1]

    empty_queue(redis_connection, queue)
    
if __name__ == "__main__":
    main()
