#!/bin/bash

# Default number of servers if not specified
num_servers=${1:-3}

echo "Launching $num_servers pairs of Pyro insult/filter services..."

# Find virtual environment in current directory
find_venv() {
    for dir in venv env .venv .env; do
        if [ -d "$dir" ] && [ -f "$dir/bin/activate" ]; then
            echo "$dir"
            return 0
        fi
    done
    echo ""
    return 1
}

VENV_DIR=$(find_venv)

if [ -z "$VENV_DIR" ]; then
    echo "Virtual environment not found. Using system Python."
    PYTHON_CMD="python3"
else
    echo "Using virtual environment at $VENV_DIR"
    PYTHON_CMD="source $VENV_DIR/bin/activate && python"
fi

# Function to open a terminal and run a command
open_terminal() {
    title="$1"
    command="$2"

    # Try to detect terminal
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

# Check if pyro-ns is running, start if not
if ! pgrep -f "python.*-m.*Pyro4.naming" > /dev/null; then
    echo "Starting Pyro4 name server..."
    open_terminal "Pyro4 Name Server" "$PYTHON_CMD -m Pyro4.naming" &
    sleep 3  # Give the name server time to start
fi

# Add a small delay between starting services
SERVICE_START_DELAY=2

# Kill existing Pyro services
cleanup() {
    echo "Cleaning up existing Pyro services..."
    pkill -f "python.*Pyro/insult_service.py" || true
    pkill -f "python.*Pyro/insult_filter.py" || true
    sleep 1
}

# Clean up existing processes
cleanup

# Current directory path (for use in commands)
CURRENT_DIR=$(pwd)

# Launch insult services
for ((i=0; i<num_servers; i++)); do
    title="Pyro Insult Service $i"
    command="cd $CURRENT_DIR && $PYTHON_CMD -u Pyro/insult_service.py $i"
    open_terminal "$title" "$command"
    sleep $SERVICE_START_DELAY
done

# Launch filter services
for ((i=0; i<num_servers; i++)); do
    title="Pyro Filter Service $i"
    command="cd $CURRENT_DIR && $PYTHON_CMD -u Pyro/insult_filter.py $i"
    open_terminal "$title" "$command"
    sleep $SERVICE_START_DELAY
done

echo "All Pyro services launched in separate terminals"
echo "To check registered services, run: $PYTHON_CMD -m Pyro4.nsc list"
echo "To stop all services at once, run: killall -9 python"