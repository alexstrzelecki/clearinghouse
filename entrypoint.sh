#!/bin/sh

if [ "$DEV_MODE" = "True" ]; then
    echo "Running in development mode"
    exec fastapi dev --host 0.0.0.0 src/uv_docker_example
else
    echo "Running in production mode"
    exec fastapi run main.py --port 80
fi
