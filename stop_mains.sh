#!/bin/bash

# Stop Python program 1
if [ -f /tmp/main_alarms.pid ]; then
    kill $(cat /tmp/main_alarms.pid)
    rm /tmp/main_alarms.pid
else
    echo "PID file for main_alarms.py not found."
fi

# Stop Python program 2
if [ -f /tmp/main_saveraw.pid ]; then
    kill $(cat /tmp/main_saveraw.pid)
    rm /tmp/main_saveraw.pid
else
    echo "PID file for main_saveraw.py not found."
fi

# Stop Python program 3
if [ -f /tmp/websocket_server.pid ]; then
    kill $(cat /tmp/websocket_server.pid)
    rm /tmp/websocket_server.pid
else
    echo "PID file for websocket_server.py not found."
fi
