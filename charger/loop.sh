#!/bin/bash

# Use Python venv
source /opt/solar-controller/venv/bin/activate

# Define adapters
adapters=()
adapters+=("can0")
adapters+=("can1")

# Set up traps
#trap cleanup_routine SIGINT SIGTERM EXIT
#trap cleanup_routine SIGINT SIGTERM TSTP

# Cleanup function
function cleanup_routine() {
   # Reconfigure all adapters
   for adapter in "${adapters[@]}"
   do
       echo "Bring down adapter <$adapter>"
       sudo ip link set down $adapter
   done
}

# Reconfigure all adapters
for adapter in "${adapters[@]}"
do
    echo "Re-initialize and re-configure adapter <$adapter>"
    #sudo ip link set down $adapter
    #sleep 0.5
    #sudo ip link set $adapter type can bitrate 125000 restart-ms 1500
    #sleep 0.5
    #sudo ip link set up $adapter
    #sudo /opt/solar-controller/venv/bin/python ./rectifier.py --interface "$adapter" -C
    sudo python ./rectifier.py --interface "$adapter" -C
done

# Loop
while true
do
    for adapter in "${adapters[@]}"
    do
        #./emerson-r48.py
        #./rectifier.py "$adapter" 56.0
        #./rectifier.py --interface "$adapter" --voltage 56.0 --current 20.0 --permanent False
        #sudo /opt/solar-controller/venv/bin/python ./rectifier.py --mode "set" --interface "$adapter" --voltage 56.0 --current_value 50.0
        sudo python ./rectifier.py --mode "set" --interface "$adapter" --voltage 56.0 --current_value 50.0
        sleep 10
    done
done
