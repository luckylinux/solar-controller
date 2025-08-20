#!/bin/bash

# Change to app folder
cd "/opt/app" || exit

# Start the main process and save its PID
# Use exec to replace the shell script process with the main process
exec "/opt/app/app.sh" &
pidh=$!

# Trap the SIGTERM signal and forward it to the main process
trap 'kill -SIGTERM $pidh; wait $pidh' SIGTERM

# Wait for the main process to complete
wait $pidh
