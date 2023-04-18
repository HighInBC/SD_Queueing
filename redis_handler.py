import redis
import json
import time

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

def read_from_ingress_queue(redis_connection, base_queue_name):
    """
    Read a job from the ingress queues using the Redis connection object.
    Return the job request and the client-specific return queue.
    """
    ingress_queues = [
        f"{base_queue_name}_priority_{i}" for i in range(5, -1, -1)
    ]
    while True:
        for queue_name in ingress_queues:
            job = redis_connection.blpop(queue_name, timeout=0.01)
            if job is not None:
                job = json.loads(job[1])
                return job
        time.sleep(.25)

def send_response_to_return_queue(redis_connection, return_queue, original_request, response):
    """
    Package the original request and response (array of base64 images) in a JSON object.
    Send the JSON object to the client-specific return queue using the Redis connection object.
    """
    response_obj = {
        "request": original_request,
        "response": response
    }
    response_str = json.dumps(response_obj)
    redis_connection.rpush(return_queue, response_str)

def send_job_to_ingress_queue(redis_connection, base_queue_name, payload, return_queue, label, priority=0):
    """
    Send a job to the ingress queue using the Redis connection object.
    The priority should be an integer between 0 and 5, where 0 is the lowest priority and 5 is the highest.
    """
    if priority < 0:
        priority = 0
    if priority > 5:
        priority = 5
    queue_name = f"{base_queue_name}_priority_{priority}"
    job = {"payload":payload, "return_queue":return_queue, "label":label}
    job_str = json.dumps(job)
    redis_connection.rpush(queue_name, job_str)

def read_from_return_queue(redis_connection, return_queue, timeout=None):
    """
    Read a response from the client-specific return queue using the Redis connection object.
    Blocks until the response is available or the optional timeout is reached.
    Returns a dictionary containing the original request and the response (array of base64 images).
    """
    response = redis_connection.blpop(return_queue, timeout=timeout)
    if response is not None:
        response_obj = json.loads(response[1])
        return response_obj
    else:
        return None