#!/bin/bash

# Temporary fix
export PATH="$PATH:/home/unmined-cli_0.19.37-dev_linux-x64"

excluded_dirs=("cache" "libraries" "versions")
secretNames=("FTP_HOSTNAME_SECRET" "FTP_USERNAME_SECRET" "FTP_PASSWORD_SECRET")
config_file="worlds.json"

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

# Split FTP_HOSTNAME_SECRET into hostname and port if port is specified
if [[ "${secrets["FTP_HOSTNAME_SECRET"]}" == *:* ]]; then
    IFS=':' read -r hostname port <<< "${secrets["FTP_HOSTNAME_SECRET"]}"
else
    hostname="${secrets["FTP_HOSTNAME_SECRET"]}"
    port=""
fi

excludes=$(for dir in "${excluded_dirs[@]}"; do echo -n "--exclude $dir "; done)

# Sync the FTP server with the local directory
lftp -e "set ftp:ssl-force true;\
set ftp:ssl-protect-data true;\
set ssl:verify-certificate no;\
open -u${port:+ -p $port} '${secrets["FTP_USERNAME_SECRET"]}','${secrets["FTP_PASSWORD_SECRET"]}' '${hostname}';\
mirror --only-newer --verbose $excludes --parallel=10 / $MOUNT_PATH;\
exit"

if [[ $? -ne 0 ]]; then
    echo "Failed to sync with FTP server"
    exit 1
fi

# Render the maps and edit the file paths to be served correctly
worlds=$(jq -r 'keys[]' $config_file)

for world in $worlds; do
    options_keys=$(jq -r --arg world "$world" '.[$world].options | keys[]' $config_file)
    options=""
    for key in $options_keys; do
        value=$(jq -r --arg world "$world" --arg key "$key" '.[$world].options[$key]' $config_file)
        options+="--$key $value "
    done
    path=$(jq -r --arg world "$world" '.[$world].path' $config_file)
    eval "unmined-cli web render $options"
    find "$RENDER_OUTPUT_PATH/$world" -name "unmined.index.html" -type f -exec sed -i 's|<title>.*</title>|<title>Iriserver</title>|g' {} \;
    find "$RENDER_OUTPUT_PATH/$world" -name "unmined.index.html" -type f -exec sed -i "s|src=\"unmined|src=\"$path/unmined|g" {} \;
    find "$RENDER_OUTPUT_PATH/$world" -name "unmined.openlayers.js" -type f -exec sed -i "s|tiles/zoom|$path/tiles/zoom|g" {} \;
    find "$RENDER_OUTPUT_PATH/$world" -name "unmined.openlayers.js" -type f -exec sed -i "s|playerimages|$path/playerimages|g" {} \;
done