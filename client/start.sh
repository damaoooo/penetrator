if [ `whoami` != "root" ];then
    print_message "Please run this script as root user!" "$RED"
	exit
fi

if command -v docker &> /dev/null; then
    print_message "Docker is already installed!" "$GREEN"
else
    print_message "Docker is not installed! Will Install it..." "$RED"
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh --mirror Aliyun
    rm get-docker.sh

fi

# Install jq
apt-get update && apt-get install -y jq

# Edit /etc/docker/daemon.json to add registry mirrors
if [ ! -f /etc/docker/daemon.json ]; then
    echo '{"registry-mirrors": ["https://docker.1ms.run"]}' > /etc/docker/daemon.json
else
    jq '. + {"registry-mirrors": ["https://docker.1ms.run"]}' /etc/docker/daemon.json > /tmp/daemon.json && mv /tmp/daemon.json /etc/docker/daemon.json
fi

# Restart Docker to apply changes
systemctl daemon-reload
systemctl restart docker

# Pull the image
docker pull gogost/gost:3.0.0-rc8
docker pull ghcr.io/xtls/xray-core
docker pull certbot/dns-cloudflare
docker pull tobyxdd/hysteria
docker pull nginx
docker pull metacubex/mohimo
