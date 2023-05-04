import redis
import json
import time
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError
from sdq.config_parser import ConfigParser

class TunnelCreationException(Exception):
    pass

class InvalidInputException(Exception):
    pass

def create_ssh_tunnel(config):
    if not isinstance(config, ConfigParser):
        raise TunnelCreationException("Config must be an instance of the ConfigParser class.")

    ssh_tunnel_config = config.ssh_tunnel
    if not ssh_tunnel_config:
        raise TunnelCreationException("Missing SSH tunnel configuration.")

    try:
        print("Creating SSH tunnel to {}@{}:{}".format(
            config.ssh_tunnel_username,
            config.ssh_tunnel_host,
            config.ssh_tunnel_port
        ))
        tunnel = SSHTunnelForwarder(
            (config.ssh_tunnel_host, config.ssh_tunnel_port),
            ssh_username=config.ssh_tunnel_username,
            ssh_pkey=config.ssh_tunnel_key_file,
            remote_bind_address=(
                config.ssh_tunnel_remote_bind_address,
                config.ssh_tunnel_remote_bind_port
            )
        )
        tunnel.start()
        print("SSH tunnel started.")
        return tunnel.local_bind_port
    except AttributeError as e:
        missing_key = str(e).split("'")[1]  # Extract the attribute name from the exception message
        raise TunnelCreationException(f"Missing required attribute in config: {missing_key}")
    except BaseSSHTunnelForwarderError as e:
        raise TunnelCreationException(f"Failed to create SSH tunnel: {e}")
    except Exception as e:
        raise TunnelCreationException(f"Unexpected error occurred while creating SSH tunnel: {e}")
    
def connect_to_redis(config):
    if not isinstance(config, ConfigParser):
        raise InvalidInputException("Config must be an instance of the ConfigParser class.")

    redis_host = config.redis_host
    redis_port = config.redis_port

    if config.ssh_tunnel:
        redis_host = "127.0.0.1"
        redis_port = create_ssh_tunnel(config)

    if not redis_host or not redis_port:
        raise InvalidInputException("Config is missing required keys: redis_host and/or redis_port")

    try:
        redis_connection = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            password=config.redis_password,
            decode_responses=True
        )
        if not redis_connection.ping():
            raise Exception("Unable to ping the Redis server.")
    except Exception as e:
        raise InvalidInputException(f"Failed to connect to Redis: {e}")

    return redis_connection

def read_from_ingress_queue(redis_connection, base_queue_name, min_priority=0):
    if not isinstance(redis_connection, redis.StrictRedis):
        raise InvalidInputException("Invalid Redis connection object.")
    if not isinstance(base_queue_name, str):
        raise InvalidInputException("Base queue name must be a string.")

    ingress_queues = [f"{base_queue_name}_priority_{i}" for i in range(5, min_priority - 1, -1)]
    while True:
        for queue_name in ingress_queues:
            job = redis_connection.lpop(queue_name)
            if job is not None:
                print(f"Received job from {queue_name}.")
                job = json.loads(job)
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

def send_job_to_ingress_queue(redis_connection, base_queue_name, payloads, return_queue, label, priority=0):
    if not isinstance(redis_connection, redis.StrictRedis):
        raise InvalidInputException("Invalid Redis connection object.")
    if not isinstance(base_queue_name, str):
        raise InvalidInputException("Base queue name must be a string.")
    if not isinstance(return_queue, str):
        raise InvalidInputException("Return queue must be a string.")
    if not isinstance(priority, int) or priority < 0 or priority > 5:
        raise InvalidInputException("Priority must be an integer between 0 and 5.")

    if not isinstance(payloads, list):
        payloads = [payloads]

    queue_name = f"{base_queue_name}_priority_{priority}"

    jobs_str = [json.dumps({"payload": payload, "return_queue": return_queue, "label": label}) for payload in payloads]
    redis_connection.rpush(queue_name, *jobs_str)

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