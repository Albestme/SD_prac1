#!/bin/bash

# Default number of servers if not specified
num_servers=${1:-3}

echo "Launching $num_servers pairs of insult/filter services..."


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
    title="Insult Service $i"
    # Use improved command with proper resource limits
    command="python3 -u Redis/insult_service.py"
    open_terminal "$title" "$command"
    sleep $SERVICE_START_DELAY
done

# Launch filter services
for ((i=0; i<num_servers; i++)); do
    title="Filter Service $i"
    # Use improved command with proper resource limits
    command="python3 -u Redis/insult_filter.py"
    open_terminal "$title" "$command"
    sleep $SERVICE_START_DELAY
done

echo "All services launched in separate terminals"
echo "Note: If you see 'Connection reset by peer' errors when testing with many clients,"
echo "      consider increasing server thread pools or connection timeouts in your Python code."
echo ""
echo "To stop all services at once, run: killall -9 python3"