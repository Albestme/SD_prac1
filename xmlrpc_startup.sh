#!/bin/bash

num_servers=${1:-3}

echo "Launching $num_servers pairs of insult/filter services..."

# Check if services are already running on ports
cleanup() {
    echo "Checking for existing services..."
    for ((i=0; i<num_servers; i++)); do
        insult_port=$((8000 + i))
        filter_port=$((8003 + i))
        pid_insult=$(lsof -ti:$insult_port)
        pid_filter=$(lsof -ti:$filter_port)

        if [ ! -z "$pid_insult" ]; then
            echo "Killing existing insult service on port $insult_port (PID: $pid_insult)"
            kill $pid_insult
            sleep 0.5
        fi

        if [ ! -z "$pid_filter" ]; then
            echo "Killing existing filter service on port $filter_port (PID: $pid_filter)"
            kill $pid_filter
            sleep 0.5
        fi
    done
}

# Clean up existing processes
cleanup

pids=()

launch() {
    python3 "$@" &
    local pid=$!
    if [ $? -eq 0 ]; then
        echo "Started: $@ (PID: $pid)"
        pids+=($pid)
    else
        echo "Failed to start: $@"
    fi
    sleep 1
}

# Launch insult services
for ((i=0; i<num_servers; i++)); do
    port=$((8000 + i))
    launch XMLRPC/insult_service.py $port
done

# Launch filter services
for ((i=0; i<num_servers; i++)); do
    filter_port=$((8003 + i))
    insult_port=$((8000 + i))
    launch XMLRPC/insult_filter.py $filter_port $insult_port
done

# Function to kill all processes
kill_all() {
    echo "Stopping all services..."
    for pid in "${pids[@]}"; do
        if kill -0 $pid 2>/dev/null; then
            echo "Killing process $pid"
            kill $pid
        fi
    done
    exit 0
}

# Register trap for cleanup
trap kill_all INT TERM EXIT

echo "Services are running in background"
echo "Press Ctrl+C to stop all services"

while true; do
    sleep 1
done