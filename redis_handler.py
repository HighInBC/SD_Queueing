# redis_handler.py

import redis

def connect_to_redis(config):
    """
    Connect to the Redis server using the configuration and return the connection object.
    """
    redis_connection = redis.StrictRedis(
        host=config["redis_host"],
        port=config["redis_port"],
        password=config["redis_password"],
        decode_responses=True
    )
    return redis_connection

def read_from_ingress_queue(redis_connection, ingress_queue):
    """
    Read a job from the ingress queue using the Redis connection object.
    Return the job request and the client-specific return queue.
    """
    pass

def send_response_to_return_queue(redis_connection, return_queue, original_request, response):
    """
    Package the original request and response (array of base64 images) in a JSON object.
    Send the JSON object to the client-specific return queue using the Redis connection object.
    """
    pass