#!/bin/bash

# Update the package list and install the required packages
sudo apt-get update
sudo apt-get install -y
sudo apt-get install lftp -y

# Install Azure CLI
if ! command -v az &> /dev/null; then
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

# Install Unmined CLI
if ! command -v unmined-cli &> /dev/null; then
    wget -O unmined-cli_0.19.37-dev_linux-x64.tar.gz https://unmined.net/download/unmined-cli-linux-x64-dev/
    gunzip unmined-cli_0.19.37-dev_linux-x64.tar.gz
    tar -xvf unmined-cli_0.19.37-dev_linux-x64.tar
    export PATH="$PATH:$(pwd)/unmined-cli_0.19.37-dev_linux-x64"
fi

# Login to Azure as the system-assigned managed identity
az login --identity