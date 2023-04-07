#!/bin/bash
set -e 
exec gunicorn app.app:app  --bind 0.0.0.0:9000 --worker-class uvicorn.workers.UvicornWorker