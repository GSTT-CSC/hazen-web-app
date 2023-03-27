#!/bin/bash

# Start the first process
celery -A hazen.worker worker &

# Start the second process
python hazen.py &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?