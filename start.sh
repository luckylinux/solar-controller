#!/bin/bash

# Change working directory
cd charger/

# Make sure everything is stopped
./cleanup.sh

# Start looping
./loop.sh
