#!/bin/bash

# Start script for VFExtractor

# Configurable ports
STREAMLIT_PORT=8501

# Function to check if a port is free
function check_port() {
    if lsof -i:$1 >/dev/null; then
        echo "Port $1 is in use. Please free it before running this script."
        exit 1
    fi
}

# Check ports
check_port $STREAMLIT_PORT

# Start Streamlit app
echo "Starting Streamlit app at http://127.0.0.1:$STREAMLIT_PORT..."
streamlit run app/app.py --server.port $STREAMLIT_PORT --server.headless true &
STREAMLIT_PID=$!

# 3. Open browsers automatically
if command -v xdg-open >/dev/null; then
    xdg-open http://127.0.0.1:$STREAMLIT_PORT
elif command -v open >/dev/null; then  # macOS
    open http://127.0.0.1:$STREAMLIT_PORT
fi

# 4. Wait for Ctrl+C to stop 
trap "echo 'Stopping servers...'; kill $STREAMLIT_PID; exit 0" SIGINT SIGTERM

# Wait indefinitely
wait
