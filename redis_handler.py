# redis_handler.py
import redis
import json

def connect_to_redis(config):
    """
    Connect to the Redis server using the configuration and return the connection object.
    """
    redis_connection = redis.StrictRedis(
        host=config["redis_host"],
        port=config["redis_port"],
        password=config.get("redis_password", None),
        decode_responses=True
    )
    return redis_connection

def read_from_ingress_queue(redis_connection, ingress_queue):
    """
    Read a job from the ingress queue using the Redis connection object.
    Return the job request and the client-specific return queue.
    """
    job = redis_connection.blpop(ingress_queue, timeout=0)
    if job is not None:
        # Parse the job as a JSON object
        job = json.loads(job[1])
        request = job.get("request")
        return_queue = job.get("return_queue")
        return request, return_queue
    else:
        # If no job is found, return None
        return None, None

import json

def send_response_to_return_queue(redis_connection, return_queue, original_request, response):
    """
    Package the original request and response (array of base64 images) in a JSON object.
    Send the JSON object to the client-specific return queue using the Redis connection object.
    """
    response_obj = {
        "request": original_request,
        "response": response
    }
    # Convert the response object to a JSON string
    response_str = json.dumps(response_obj)

    # Send the response to the client-specific return queue
    redis_connection.rpush(return_queue, response_str)
