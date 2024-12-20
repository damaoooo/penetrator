#!/bin/bash

read -p "Target URL: " target_url
read -p "Gost Bind Port: " bind_port
read -p "Password: " password
read -p "node ID: " node_id
read -p "interval (default 1800): " interval
interval=${interval:-1800}


# update into .env
echo "TARGET_URL=${target_url}" > .env
echo "BIND_PORT=${bind_port}" >> .env
echo "PASSWORD=${password}" >> .env
echo "NODE_ID=${node_id}" >> .env
echo "INTERVAL=${interval}" >> .env

# start relay
docker compose up