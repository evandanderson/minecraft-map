# Update the package list and install the required packages
sudo apt-get update
sudo apt-get install -y
sudo apt install python3.10-venv -y

# Install Azure CLI
if ! command -v az &> /dev/null; then
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

# Create the virtual environment
if ! [ -d ".venv" ]; then
    python3 -m venv .venv
fi

# Install Python dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Login to Azure as the system-assigned managed identity
az login --identity