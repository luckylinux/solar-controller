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
	# Get reference value
        voltage_reference_file="/opt/solar-controller/tmp/set_voltage"
        if [[ -f "${voltage_reference_file}" ]]; then
            set_voltage=$(cat ${voltage_reference_file})
        else
            set_voltage="51.6"
        fi

        current_reference_file="/opt/solar-controller/tmp/set_current"
        if [[ -f "${current_reference_file}" ]]; then
            set_current=$(cat ${current_reference_file})
        else
            set_current="50"
        fi

	echo "Set Output Voltage to ${set_voltage} VDC"
	echo "Set Output Current to ${set_current} ADC"

        #./emerson-r48.py
        #./rectifier.py "$adapter" 56.0
        #./rectifier.py --interface "$adapter" --voltage 56.0 --current 20.0 --permanent False
        #sudo /opt/solar-controller/venv/bin/python ./rectifier.py --mode "set" --interface "$adapter" --voltage 56.0 --current_value 50.0
#        sudo python ./rectifier.py --mode "set" --interface "$adapter" --voltage 54.6 --current_value 50.0
#        sudo python ./rectifier.py --mode "set" --interface "$adapter" --voltage 51.6 --current_value 50.0
        sudo python ./rectifier.py --mode "set" --interface "$adapter" --voltage ${set_voltage} --current_value ${set_current}
    done

    # Wait 5 seconds
    sleep 5
done
