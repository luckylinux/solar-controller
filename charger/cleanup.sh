#!/bin/bash

# Kill old process
OLDPID=$(ps aux | grep "/bin/bash ./loop.sh" | head -1 | awk {'print $2'})
sudo kill -9 $OLDPID

# Bring down all adapters
for adapter in "${adapters[@]}"
do
   echo "Bring down adapter <$adapter>"
   sudo ip link set down $adapter
done
