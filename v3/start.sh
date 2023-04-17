#!/bin/bash
# docker run --name postgre --rm -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=123 -e PGDATA=/var/lib/postgresql/data/pgdata -v /tmp:/var/lib/postgresql/data -p 54321:5432 -it postgres:14.1-alpine
python3 -m uvicorn main:app --reload --port 1337 --host 0.0.0.0