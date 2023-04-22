#!/bin/bash
server=$1
if [ "$server" == "uvicorn" ]; then
    python3 -m uvicorn main:app --reload --port 1337 --host 0.0.0.0
elif [ "$server" == "gunicorn" ]; then
    python3 -m gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:1337
else
    echo "Missing parameter, usage ./start.sh [uvicorn|gunicorn]"
    exit 1
fi