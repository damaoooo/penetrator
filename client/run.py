import requests
import argparse
import json
import logging

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

def main():
    args = parse_args()

    # Create a client instance with parsed arguments
    client = ClientRun(args.url, args.password, args.target_port)

    # Step 1: Get the session key
    client.get_session_key()

    # Step 2: Get the node list
    client.get_node_list()


if __name__ == "__main__":
    main()
