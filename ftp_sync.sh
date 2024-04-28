#!/bin/bash

# Temporary fix
export PATH="$PATH:/home/unmined-cli_0.19.37-dev_linux-x64"

excluded_dirs=("cache" "libraries" "versions")
secretNames=("FTP_HOSTNAME_SECRET" "FTP_USERNAME_SECRET" "FTP_PASSWORD_SECRET")

declare -A secrets

# Login to Azure as the system-assigned managed identity
az login --identity

# Retrieve secrets from Azure Key Vault
for secretName in "${secretNames[@]}"; do
    secretValue=$(az keyvault secret show --vault-name "$VAULT_NAME" --name "${!secretName}" --query "value" --output tsv)
    if [[ $? -ne 0 ]]; then
        echo "Failed to retrieve secret '$secretName'"
        exit 1
    fi
    secrets[$secretName]=$secretValue
done

excludes=$(for dir in "${excluded_dirs[@]}"; do echo -n "--exclude $dir "; done)

# Sync the FTP server with the local directory
lftp -e "set ftp:ssl-force true;\
set ftp:ssl-protect-data true;\
set ssl:verify-certificate no;\
open -u '${secrets["FTP_USERNAME_SECRET"]}','${secrets["FTP_PASSWORD_SECRET"]}' '${secrets["FTP_HOSTNAME_SECRET"]}';\
mirror --only-newer --verbose $excludes --parallel=10 / $MOUNT_PATH;\
exit"

if [[ $? -ne 0 ]]; then
    echo "Failed to sync with FTP server"
    exit 1
fi

# Render the map
unmined-cli web render --world "$MOUNT_PATH/world" --output "$RENDER_OUTPUT_PATH"