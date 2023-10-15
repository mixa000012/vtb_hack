#!/bin/bash

alembic upgrade head

python fill.py

uvicorn app.main:app --host=0.0.0.0 --port 8000 --ssl-keyfile="privkey.pem" --ssl-certfile="fullchain.pem"
