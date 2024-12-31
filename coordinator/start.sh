#!/bin/bash

read -p "Gost Bind Port: " bind_port
read -p "Password: " password
read -e -p "Clash File Path: " clash_file_path

# update into .env
echo "BIND_PORT=${bind_port}" > .env
echo "PASSWORD=${password}" >> .env
echo "CLASH_FILE_PATH=${clash_file_path}" >> .env


# start relay
docker compose up