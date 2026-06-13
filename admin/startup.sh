#!/bin/bash
# Wait for server to be ready, then open browser
PORT=8100
MAX_WAIT=15

for i in $(seq 1 $MAX_WAIT); do
    if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
        open "http://localhost:$PORT"
        exit 0
    fi
    sleep 1
done
