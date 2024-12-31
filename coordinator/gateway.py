import argparse
import json
import uuid
from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
from fastapi import Cookie, HTTPException, Depends
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired



# 使用 argparse 获取命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description="FastAPI Server for Clash File and Relay Management")
    parser.add_argument('--secret-key', type=str, required=True, help="Secret key for signing session keys")
    return parser.parse_args()

format_string_full = "%Y-%m-%dT%H:%M:%S.%f"
# 解析命令行参数
args = parse_args()

# 创建 FastAPI 应用
app = FastAPI()

# 初始化 itsdangerous 的序列化器
serializer = URLSafeTimedSerializer(args.secret_key, salt="session-key-salt")  # Removed max_age here

# 模拟存储的节点信息和用户认证
# 模拟存储的节点信息和用户认证


relay_list = {
    "aaa": {"ip": "1.2.3.4", "port": 12345, "last_seen": datetime.now().strftime(format_string_full)},
}
user_password = args.secret_key


# Pydantic模型用于验证请求体
class NodeInfo(BaseModel):
    node_id: str
    ip: str
    port: int

# Pydantic model to parse the incoming password
class PasswordRequest(BaseModel):
    password: str

# 验证密码，生成 sessionKey
@app.post("/verification")
async def verify_password(request: PasswordRequest):
    if request.password == user_password:
        # 生成一个带过期时间的 sessionKey
        session_key = serializer.dumps({"session_id": str(uuid.uuid4())})
        return JSONResponse(content={"sessionKey": session_key})
    else:
        raise HTTPException(status_code=400, detail="Invalid password")



# 用户认证验证（从 Cookie 中读取 sessionKey）
def verify_session(session_key: str = Cookie(None)):  # Use Cookie to get session_key
    if not session_key:
        raise HTTPException(status_code=403, detail="Session key is missing")

    try:
        # 验证 sessionKey 并检查过期
        session_data = serializer.loads(session_key, max_age=3600)  # Set max_age here (1 hour)
        return session_data
    except BadSignature:
        raise HTTPException(status_code=403, detail="Invalid session or session expired")
    except SignatureExpired:
        raise HTTPException(status_code=403, detail="Session expired")


# 获取 Clash 配置文件内容
@app.get("/clash_file")
async def get_clash_file(session_key: str = Depends(verify_session)):
    try:
        with open("/clash.yml", 'r') as f:
            clash_file_content = f.read()
        return JSONResponse(content={"clash_file": clash_file_content})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Clash file not found")


# 获取 relay 节点信息
@app.get("/relay_list")
async def get_relay_list(session_key: str = Depends(verify_session)):
    # 删除超时的节点
    global relay_list
    timeout = timedelta(minutes=30)
    now = datetime.now()
    relay_list = {k: v for k, v in relay_list.items() if now - datetime.strptime(v["last_seen"], format_string_full) < timeout}
    return JSONResponse(content={"relay_list": relay_list})


# 更新 relay 节点信息
@app.post("/update_node")
async def update_node(node_info: NodeInfo, session_key: str = Depends(verify_session)):
    global relay_list
    # 更新或添加节点信息
    relay_list[node_info.node_id] = {
        "ip": node_info.ip,
        "port": node_info.port,
        "last_seen": datetime.now().strftime(format_string_full)
    }
    return JSONResponse(content={"message": "Node updated successfully"})


# 启动 FastAPI 应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
