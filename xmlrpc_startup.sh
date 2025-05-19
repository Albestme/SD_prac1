#!/bin/bash

# Default number of servers if not specified
num_servers=${1:-3}

echo "Launching $num_servers pairs of insult/filter services..."

# Check and kill any existing services
cleanup() {
    echo "Checking for existing services..."
    for ((i=0; i<num_servers; i++)); do
        insult_port=$((8000 + i))
        filter_port=$((8003 + i))

        pid_insult=$(lsof -ti:$insult_port 2>/dev/null)
        if [ ! -z "$pid_insult" ]; then
            echo "Killing existing insult service on port $insult_port (PID: $pid_insult)"
            kill $pid_insult
            sleep 0.5
        fi

        pid_filter=$(lsof -ti:$filter_port 2>/dev/null)
        if [ ! -z "$pid_filter" ]; then
            echo "Killing existing filter service on port $filter_port (PID: $pid_filter)"
            kill $pid_filter
            sleep 0.5
        fi
    done
}

# Clean up existing processes first
cleanup

# Function to open a terminal and run a command
open_terminal() {
    title="$1"
    command="$2"

    # Try to detect your terminal
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$title" -- bash -c "$command; echo 'Press Enter to close...'; read"
    elif command -v konsole &> /dev/null; then
        konsole --title="$title" -e bash -c "$command; echo 'Press Enter to close...'; read"
    elif command -v xfce4-terminal &> /dev/null; then
        xfce4-terminal --title="$title" -e "bash -c \"$command; echo 'Press Enter to close...'; read\""
    elif command -v xterm &> /dev/null; then
        xterm -T "$title" -e "bash -c \"$command; echo 'Press Enter to close...'; read\""
    else
        echo "No supported terminal found. Please install gnome-terminal, konsole, xfce4-terminal, or xterm."
        exit 1
    fi
}

# Add a small delay between starting services to avoid overwhelming the system
SERVICE_START_DELAY=2

# Launch insult services with more resources
for ((i=0; i<num_servers; i++)); do
    port=$((8000 + i))
    title="Insult Service $i (Port $port)"
    # Use improved command with proper resource limits
    command="python3 -u XMLRPC/insult_service.py $port"
    open_terminal "$title" "$command"
    sleep $SERVICE_START_DELAY
done

# Launch filter services
for ((i=0; i<num_servers; i++)); do
    filter_port=$((8003 + i))
    insult_port=$((8000 + i))
    title="Filter Service $i (Ports $filter_port -> $insult_port)"
    # Use improved command with proper resource limits
    command="python3 -u XMLRPC/insult_filter.py $filter_port $insult_port"
    open_terminal "$title" "$command"
    sleep $SERVICE_START_DELAY
done

echo "All services launched in separate terminals"
echo "Note: If you see 'Connection reset by peer' errors when testing with many clients,"
echo "      consider increasing server thread pools or connection timeouts in your Python code."
echo ""
echo "To stop all services at once, run: killall -9 python3"