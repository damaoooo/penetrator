# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装必要的系统工具和 Docker CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        lsb-release \
        build-essential \
        libyaml-dev \
        libffi-dev \
        libssl-dev \
        git \
        docker.io && \
    rm -rf /var/lib/apt/lists/*

# 安装 Docker Compose 插件
RUN curl -SL https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# 将 docker-compose 软链接为 docker compose
RUN ln -s /usr/local/bin/docker-compose /usr/local/bin/docker-compose-plugin

# 将 docker-compose-plugin 软链接为 docker compose
RUN ln -s /usr/local/bin/docker-compose-plugin /usr/local/bin/docker

# 将 requirements.txt 复制到工作目录
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码到工作目录
COPY . /app

