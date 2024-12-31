import requests
import argparse
import json
import yaml
import logging
from typing import Union

# 设置日志配置
log_filename = "client_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),  # 日志保存到文件
        logging.StreamHandler()  # 同时输出到控制台
    ]
)


def parse_args():
    parser = argparse.ArgumentParser(description='Client for running the server')
    parser.add_argument('--url', type=str, help='URL of the server', required=True)
    parser.add_argument('--target_port', type=int, help='Target Port number of the server', required=True)
    parser.add_argument('--password', type=str, help='Password for the server', required=True)
    parser.add_argument('--inner-domain', type=str, help='Inner domain name', required=True)
    return parser.parse_args()


class ClientRun:
    def __init__(self, url: str, password: str, target_port: int):
        self.url = url
        self.password = password
        self.target_port = target_port
        self.session_key = None

    def get_session_key(self):
        # Step 1: Get the sessionKey by sending the password to the server
        endpoint = f"{self.url}/verification"
        payload = {'password': self.password}
        try:
            logging.info("Requesting sessionKey...")
            response = requests.post(endpoint, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.session_key = data.get("sessionKey")
                logging.info(f"SessionKey obtained successfully: {self.session_key}")
            else:
                logging.error(f"Failed to obtain sessionKey. Status code: {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Error while obtaining sessionKey: {e}")

    def get_node_list(self):
        if not self.session_key:
            logging.warning("SessionKey is missing. Please obtain a sessionKey first.")
            return

        # Step 2: Get the node list using the sessionKey as a Cookie
        endpoint = f"{self.url}/relay_list"
        headers = {'Content-Type': 'application/json'}
        cookies = {'session_key': self.session_key}

        try:
            logging.info(f"Fetching node list from {self.url}/relay_list using sessionKey...")
            response = requests.get(endpoint, headers=headers, cookies=cookies)
            if response.status_code == 200:
                node_list = response.json()
                logging.info("Node List obtained successfully:")
                logging.info(json.dumps(node_list, indent=4))
                return node_list
            if response.status_code == 403:
                logging.info("SessionKey is invalid. Please obtain a new sessionKey.")
                self.get_session_key()
                # self.get_node_list()
            else:
                logging.error(f"Failed to fetch node list. Status code: {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Error while fetching node list: {e}")
        return None
    
    def update_docker_compose(self):
        
        services = [{
                'hysteria2': {
                'image': 'tobyxdd/hysteria',
                'restart': 'always',
                'ports': ['12306:12306'],
                'volumes': [
                    './hy2_config.yaml:/etc/hysteria.yaml'
                ],
                'command': ['server', '-c', '/etc/hysteria.yaml']
                }
            }
        ]
        
        node_list = self.get_node_list()
        for node in node_list:
            services.append({
                node['name']: {
                    'image': 'tobyxdd/hysteria',
                    'container_name': node['name'],
                    'restart': 'always',
                    'network_mode': 'host',
                    'volumes': [
                        './hy2_config.yaml:/etc/hysteria.yaml'
                    ],
                    'command': ['node', '-c', '/etc/hysteria.yaml']
                }
            })


class Hy2ConfigManager:
    def __init__(self, config: Union[str, dict], cf_token: str, domain_name: str, auth_password: str):
        self.config = config
        if isinstance(config, str):
            self.config = self.load_config(config)
        self.cf_token = cf_token
        self.domain_name = domain_name
        self.auth_password = auth_password


    def load_config(self, config_file: str):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
        
    def save_config(self, config_file: str):
        with open(config_file, 'w') as f:
            yaml.dump(self.config, f)

    def update_config(self):
        self.config['acme']['domains'] = [self.domain_name]
        self.config['acme']['dns']['config']['cloudflare_api_token'] = self.cf_token
        self.config['auth']['userpass'] = [{'myself': self.auth_password}]


def get_cloudflare_token(password):
    r = requests.post("https://penetrator-worker.damaoooo.com/cf_token",
                      json={"password": password})
    if r.status_code == 200:
        return r.json()['token'], r.json()['zone_id']
    else:
        print("Get cloudflare token failed!")
        return "", ""


def get_configs(password):
    r = requests.post("https://penetrator-worker.damaoooo.com/config_file",
                      json={"password": password})
    if r.status_code == 200:
        return r.json()['hy2'], r.json()['user']
    else:
        print("Get configs failed!")
        return "", ""

def main():
    args = parse_args()
    back_end = args.url
    password = args.password
    target_port = args.target_port
    inner_domain = args.inner_domain

    password = "fuckyoub1tch"

    # Update the config file
    cf_token, zone_id = get_cloudflare_token(password)
    hy2config, user = get_configs(password)
    auth_password = user['myself']
    config_manager = Hy2ConfigManager(hy2config, cf_token, inner_domain, auth_password)
    config_manager.update_config()
    config_manager.save_config("hy2_config.yaml")
    # # Create a client instance with parsed arguments
    # client = ClientRun(back_end, password, target_port)

    # # Step 1: Get the session key
    # client.get_session_key()

    # # Step 2: Get the node list
    # client.get_node_list()


if __name__ == "__main__":
    main()
