#!/usr/bin/env python3
import sys
from sdq.redis_handler import connect_to_redis, InvalidInputException
from sdq.config_parser import ConfigParser

def main():
    config = ConfigParser(config_file='config.json')

    if len(sys.argv) != 2:
        print("Usage: ./empty_redis_queue.py <queue>")
        sys.exit(2)

    queue = sys.argv[1]

    if not queue:
        print("Error: Queue name cannot be empty")
        sys.exit(2)

    try:
        redis_connection = connect_to_redis(config)
    except InvalidInputException as e:
        print(f"Error: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

    print("Emptying queue...")
    try:
        redis_connection.delete(queue)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
