import asyncio
import aiohttp
import requests
import argparse
import logging
from datetime import datetime

# 设置日志配置
log_filename = "node_info_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)

# 获取本机公网IP
def get_public_ip():
    try:
        # 使用公共API获取公网IP
        logging.info("Fetching public IP...")
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        public_ip = response.json()['ip']
        logging.info(f"Public IP obtained: {public_ip}")
        return public_ip
    except requests.RequestException as e:
        logging.error(f"Error fetching public IP: {e}")
        return None


# 获取sessionKey
async def get_session_key(session, url, password):
    payload = {'password': password}
    try:
        logging.info("Requesting session key...")
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                response_data = await response.json()
                logging.info("SessionKey obtained successfully.")
                return response_data.get('sessionKey')
            else:
                logging.error(f"Failed to get sessionKey. Status code: {response.status}")
                return None
    except Exception as e:
        logging.error(f"Error while requesting sessionKey: {e}")
        return None


# 发送节点信息的异步函数
async def send_node_info(session, url, node_info, port):
    public_ip = get_public_ip()
    if public_ip:
        node_data = {
            'node_id': node_info['node_id'],
            'ip': public_ip,
            'port': port
        }

        # 构建POST请求，带上sessionKey作为Cookie
        headers = {'Content-Type': 'application/json'}
        cookies = {'session_key': node_info['session_key']}
        logging.info(f"Sending node info: {node_data} to {url} with sessionKey in cookies.")
        try:
            async with session.post(url, json=node_data, cookies=cookies, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    logging.info(f"Node updated successfully: {response_data['message']}")
                elif response.status == 403:  # 可能是sessionKey过期，重新获取sessionKey
                    logging.error("SessionKey expired or invalid, attempting to get a new sessionKey.")
                    new_session_key = await get_session_key(session, f"{url}/verification", node_info['password'])
                    if new_session_key:
                        node_info['session_key'] = new_session_key
                        # 重新发送请求
                        await send_node_info(session, url, node_info, port)
                else:
                    logging.error(f"Failed to update node. Status code: {response.status}")
        except Exception as e:
            logging.error(f"Error while sending request: {e}")
    else:
        logging.error("Unable to fetch public IP, skipping node info update.")


# 定时任务，30分钟发送一次请求
async def periodic_task(node_info, url, port, interval=1800):
    async with aiohttp.ClientSession() as session:
        while True:
            logging.info(f"Scheduled task: Sending node info every {interval / 60} minutes.")
            await send_node_info(session, url, node_info, port)
            logging.info(f"Waiting for the next cycle ({interval / 60} minutes)...")
            await asyncio.sleep(interval)  # 每30分钟执行一次


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Send node information to a server periodically")
    parser.add_argument('--node_id', type=str, required=True, help="The ID of the node")
    parser.add_argument('--password', type=str, required=True, help="The password for authentication")
    parser.add_argument('--port', type=int, required=True, help="The port of the node")
    parser.add_argument('--url', type=str, default="http://1.2.4.5:1234", help="The server URL")
    parser.add_argument('--interval', type=int, default=3600, help="The interval in seconds between requests")

    args = parser.parse_args()

    # 获取 sessionKey
    session_key = None

    async def get_session():
        nonlocal session_key
        async with aiohttp.ClientSession() as session:
            session_key = await get_session_key(session, f"{args.url}/verification", args.password)

    # 获取 sessionKey
    logging.info(f"Starting session key retrieval for node {args.node_id}...")
    asyncio.run(get_session())

    if session_key:
        logging.info("SessionKey obtained successfully.")
        # Node info
        node_info = {
            'node_id': args.node_id,
            'session_key': session_key,
            'password': args.password
        }

        # 启动定时任务
        logging.info("Starting periodic task to send node information...")
        asyncio.run(periodic_task(node_info, f"{args.url}/update_node", args.port, args.interval))
    else:
        logging.error("Failed to obtain sessionKey. Exiting.")


if __name__ == "__main__":
    main()
