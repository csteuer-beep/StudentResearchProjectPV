#!/bin/bash

# Start Python program 1
python3 main_alarms.py &

# Start Python program 2
python3 main_saveraw.py &

# Start Python program 3
python3 websocket_server.py &

wait

