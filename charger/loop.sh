#!/bin/bash

# Define adapters
adapters=()
adapters+=("can0")
adapters+=("can1")

# Reconfigure all adapters
for adapter in "${adapters[@]}"
do
    echo "Re-initialize and re-configure adapter <$adapter>"
    sudo ip link set down $adapter
    sleep 0.5
    sudo ip link set $adapter type can bitrate 125000 restart-ms 1500
    sleep 0.5
    sudo ip link set up $adapter
done

# Loop
while true
do
    ./emerson-r48.py
    sleep 30
done
