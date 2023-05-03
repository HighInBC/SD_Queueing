#!/usr/bin/env python3
import sys
import sdq.redis_handler
from sdq.config_parser import ConfigParser

def handle_job(job):
    print("Emptying queue...")

def main():
    config = ConfigParser(config_file='config.json')
    global counter
    counter = {}

    try:
        redis_connection = sdq.redis_handler.connect_to_redis(config)
    except sdq.redis_handler.InvalidInputException as e:
        print(f"Error: {e}")
        sys.exit(1)

    queue = sys.argv[1]

    while True:
        try:
            response = sdq.redis_handler.read_from_return_queue(redis_connection, queue)
            if response is not None:
                print("Received job:")
                handle_job(response)
            else:
                print("No job received. Exiting.")
                break
        except sdq.redis_handler.InvalidInputException as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
