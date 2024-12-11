#!/bin/bash

# Use Python venv
source /opt/solar-controller/venv/bin/activate

# Define adapters
adapters=()
#adapters+=("can0")
#adapters+=("can1")
#adapters+=("grid-charger-0")
#adapters+=("grid-charger-1")
adapters+=("grid-charger-01")
adapters+=("grid-charger-02")
adapters+=("grid-charger-03")
adapters+=("grid-charger-04")
adapters+=("grid-charger-05")

# Stop solar-controller Systemd Service
systemctl stop solar-controller

# Wait a bit
sleep 5

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
function reconfigure_adapters() {
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
}

# Run Cleanup Routine
cleanup_routine

# Reconfigure Adapters
reconfigure_adapters

# Oneshot
for adapter in "${adapters[@]}"
do
    # Set Default Values:
    # - 51.6 VDC Voltage (approx. 20-30% SOC in Open-Loop)
    # - 50.0 ADC Current Maximum
    set_voltage="51.6"
    set_current="50"

    echo "[${adapter}] Set Permanent Setting for Output Voltage to ${set_voltage} VDC"
    echo "[${adapter}] Set Permanent Settting for Output Current to ${set_current} ADC"

    sudo python ./rectifier.py --mode "set" --interface "${adapter}" --voltage "${set_voltage}" --current_value "${set_current}" --permanent
done

# Wait a bit
sleep 5

# Restart solar-controller Systemd Service
systemctl restart solar-controller
