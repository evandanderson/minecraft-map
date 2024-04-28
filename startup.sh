#!/bin/bash

# Update the package list and install the required packages
apt-get update
apt-get install -y
apt-get install lftp -y

# Install Azure CLI
if ! command -v az &> /dev/null; then
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash
fi

# Install Unmined CLI
if ! command -v unmined-cli &> /dev/null; then
    wget -O /home/unmined-cli_0.19.37-dev_linux-x64.tar.gz https://unmined.net/download/unmined-cli-linux-x64-dev/
    tar -zxvf /home/unmined-cli_0.19.37-dev_linux-x64.tar.gz -C /home
    rm /home/unmined-cli_0.19.37-dev_linux-x64.tar.gz
    export PATH="$PATH:/home/unmined-cli_0.19.37-dev_linux-x64"
fi

# Login to Azure as the system-assigned managed identity
az login --identity

# Start the server
gunicorn --bind=0.0.0.0 --timeout 600 app:app