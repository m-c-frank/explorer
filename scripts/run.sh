#!/bin/bash

# Directory to monitor
MONITOR_DIR="/home/mcfrank/notes"

# Python script to run
PYTHON_SCRIPT="server.py"
PYTHON_SCRIPT_GENERATOR="src/generator.py"

# Initial snapshot
SNAPSHOT=$(ls -lR "$MONITOR_DIR")

# Function to start or restart the Python script
restart_python_script() {
    # Kill the Python script if it is running
    pkill -f $PYTHON_SCRIPT
    # Wait a bit for the process to be killed
    sleep 1
    # Start the Python script in the background
    python $PYTHON_SCRIPT &
}

generate_new_samples() {
    python $PYTHON_SCRIPT_GENERATOR &
}

kill_port() {
    # Check if any processes are using the specified port
    processes=$(sudo lsof -t -i :8000)

    if [ -z "$processes" ]; then
        echo "No processes found using port 8000"
        return 0
    fi

    # Kill the processes
    sudo kill -9 $processes
    echo "Killed processes using port 8000"
}

cleanup() {
    kill_port
    pkill -f $PYTHON_SCRIPT
    exit 1
}

trap 'cleanup' SIGINT

# Start the Python script for the first time
restart_python_script

# Monitoring loop
while true; do
    # Take a new snapshot
    NEW_SNAPSHOT=$(ls -lR "$MONITOR_DIR")
    # Compare the old snapshot with the new one
    if [ "$SNAPSHOT" != "$NEW_SNAPSHOT" ]; then
        echo "Change detected. Restarting the Python script..."
        restart_python_script
        generate_new_samples
        # Update the snapshot
        SNAPSHOT=$NEW_SNAPSHOT
    fi
    # Wait a bit before checking again
    sleep 2
done


