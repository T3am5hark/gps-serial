#!/bin/bash

echo "Starting gps data collection"
source activate.sh
# export PYTHONPATH='.'
echo "PYTHONPATH=$PYTHONPATH"
python ./gps_main.py > /dev/null &

echo "Background collection started"
