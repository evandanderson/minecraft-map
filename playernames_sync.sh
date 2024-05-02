#!/bin/bash

player_names_file="/home/unmined-cli_0.19.37-dev_linux-x64/config/playernames.txt"

# Clear the output file
> $player_names_file

# Write player data to the output file
jq -r '.[] | "\(.uuid) \(.name)"' $MOUNT_PATH/whitelist.json >> $player_names_file
