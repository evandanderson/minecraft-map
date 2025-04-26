#!/bin/bash

VERSION="0.19.37-dev"

# Update the package list and install the required packages
apt-get update
apt-get install -y
apt-get install lftp -y

# Install Unmined CLI
if [ ! -d "/home/unmined-cli_{$VERSION}_linux-x64" ]; then #TODO: fix this lol
    wget -O /home/unmined-cli_{$VERSION}_linux-x64.tar.gz https://unmined.net/download/unmined-cli-linux-x64-dev/
    tar -zxvf /home/unmined-cli_{$VERSION}_linux-x64.tar.gz -C /home
    rm /home/unmined-cli_{$VERSION}_linux-x64.tar.gz
fi

# Add Unmined CLI to PATH
export PATH="$PATH:/home/unmined-cli_{$VERSION}_linux-x64"
