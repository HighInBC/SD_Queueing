import json

class ConfigParser:
    def __init__(self, config_file):
        self.config = None
        self.load_config(config_file)

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The configuration file '{config_file}' does not exist.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse the configuration file '{config_file}': {e}")

    @property
    def ingress_queue(self):
        return self.config.get('ingress_queue')

    @property
    def return_queue(self):
        return self.config.get('return_queue')

    @property
    def server_id(self):
        return self.config.get('server_id')

    @property
    def ssh_tunnel(self):
        return self.config.get('ssh_tunnel')

    @property
    def ssh_tunnel_host(self):
        return self.config.get('ssh_tunnel', {}).get('host')

    @property
    def ssh_tunnel_port(self):
        return self.config.get('ssh_tunnel', {}).get('port')

    @property
    def ssh_tunnel_username(self):
        return self.config.get('ssh_tunnel', {}).get('username')

    @property
    def ssh_tunnel_key_file(self):
        return self.config.get('ssh_tunnel', {}).get('key_file')

    @property
    def ssh_tunnel_remote_bind_address(self):
        return self.config.get('ssh_tunnel', {}).get('remote_bind_address')

    @property
    def ssh_tunnel_remote_bind_port(self):
        return self.config.get('ssh_tunnel', {}).get('remote_bind_port')

    @property
    def redis_host(self):
        return self.config.get('redis_host', '127.0.0.1' if self.ssh_tunnel else None)

    @property
    def redis_port(self):
        return self.config.get('redis_port')

    @property
    def redis_password(self):
        return self.config.get('redis_password')