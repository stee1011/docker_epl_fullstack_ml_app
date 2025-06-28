#!/bin/bash

set -e 

exec uvicorn fastapi_app:app --host 0.0.0.0 --port 8002 