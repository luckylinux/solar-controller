#!/bin/bash

# Change to app folder
cd "/opt/app" || exit

# Run Supercronic & Redirect Output of Children processes to Docker Log:
# https://stackoverflow.com/questions/55444469/redirecting-script-output-to-docker-logs
# supercronic -split-logs /etc/supercronic/crontab 1> /proc/1/fd/1 2> /proc/1/fd/2 &

# Set timezone using environment
ln -snf "/usr/share/zoneinfo/${TIMEZONE:-UTC}" "/etc/localtime"

# Run Python Script
python -u /opt/app/strategy.py

# Infinite loop to Troubleshoot
# (also needed if the Main Script/App doesn't have a looping itself, preventing the Container from Stopping)
if [[ "${ENABLE_INFINITE_LOOP}" == "true" ]]
then
    echo "Starting Infinite Loop"
    while true
    do
        sleep 5
    done
fi
