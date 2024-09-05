#!/bin/bash

# Start Python program 1
python3 main_alarms.py &
echo $! > /tmp/main_alarms.pid

# Start Python program 2
python3 main_saveraw.py &
echo $! > /tmp/main_saveraw.pid

# Start Python program 3
python3 websocket_server.py &
echo $! > /tmp/websocket_server.pid

# Wait for all programs to finish (optional)
wait