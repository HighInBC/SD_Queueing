#!/usr/bin/env python3
import sys
import redis
from sdq.redis_handler import connect_to_redis, InvalidInputException
from sdq.config_parser import ConfigParser

def handle_job(job):
    print("Emptying queue...")

def empty_queue(redis_connection, queue):
    print("Emptying queue...")
    redis_connection.delete(queue)

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
