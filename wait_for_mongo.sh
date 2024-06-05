#!/bin/bash

MAX_RETRIES=60
RETRY_INTERVAL=10

until python -c "import sys; from pymongo import MongoClient; client = MongoClient('mongodb.jenkins.svc.cluster.local', 27017); sys.exit(0 if client.admin.command('ping')['ok'] == 1 else 1)"
do
  echo "Waiting for MongoDB connection at mongodb.jenkins.svc.cluster.local:27017..."
  sleep $RETRY_INTERVAL
  RETRIES=$((RETRIES+1))
  if [ $RETRIES -ge $MAX_RETRIES ]; then
    echo "MongoDB did not become ready in time, exiting..."
    exit 1
  fi
done
echo "MongoDB is up and running at mongodb.jenkins.svc.cluster.local:27017"