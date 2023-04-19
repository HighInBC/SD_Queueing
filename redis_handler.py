import redis
import json
import time

class InvalidInputException(Exception):
    pass

def connect_to_redis(config):
    if not isinstance(config, dict):
        raise InvalidInputException("Config must be a dictionary.")

    required_keys = ["redis_host", "redis_port"]
    for key in required_keys:
        if key not in config:
            raise InvalidInputException(f"Config is missing required key: {key}")

    redis_connection = redis.StrictRedis(
        host=config["redis_host"],
        port=config["redis_port"],
        password=config.get("redis_password", None),
        decode_responses=True
    )
    return redis_connection

def read_from_ingress_queue(redis_connection, base_queue_name):
    if not isinstance(redis_connection, redis.StrictRedis):
        raise InvalidInputException("Invalid Redis connection object.")
    if not isinstance(base_queue_name, str):
        raise InvalidInputException("Base queue name must be a string.")

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

def send_response_to_return_queue(redis_connection, return_queue, original_request, response, server_id):
    if not isinstance(redis_connection, redis.StrictRedis):
        raise InvalidInputException("Invalid Redis connection object.")
    if not isinstance(return_queue, str):
        raise InvalidInputException("Return queue must be a string.")

    response_obj = {
        "request": original_request,
        "server_id": server_id,
        "response": response
    }
    response_str = json.dumps(response_obj)
    redis_connection.rpush(return_queue, response_str)

def send_job_to_ingress_queue(redis_connection, base_queue_name, payload, return_queue, label, priority=0):
    if not isinstance(redis_connection, redis.StrictRedis):
        raise InvalidInputException("Invalid Redis connection object.")
    if not isinstance(base_queue_name, str):
        raise InvalidInputException("Base queue name must be a string.")
    if not isinstance(return_queue, str):
        raise InvalidInputException("Return queue must be a string.")
    if not isinstance(priority, int) or priority < 0 or priority > 5:
        raise InvalidInputException("Priority must be an integer between 0 and 5.")

    queue_name = f"{base_queue_name}_priority_{priority}"
    job = {"payload": payload, "return_queue": return_queue, "label": label}
    job_str = json.dumps(job)
    redis_connection.rpush(queue_name, job_str)

def read_from_return_queue(redis_connection, return_queue, timeout=None):
    if not isinstance(redis_connection, redis.StrictRedis):
        raise InvalidInputException("Invalid Redis connection object.")
    if not isinstance(return_queue, str):
        raise InvalidInputException("Return queue must be a string.")

    response = redis_connection.blpop(return_queue, timeout=timeout)
    if response is not None:
        response_obj = json.loads(response[1])
        return response_obj
    else:
        return None