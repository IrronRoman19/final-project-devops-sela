#!/bin/bash

MAX_RETRIES=60
RETRY_INTERVAL=10

check_mongo() {
  local host=$1
  local port=$2

  until python -c "import sys; from pymongo import MongoClient; client = MongoClient('${host}', ${port}); sys.exit(0 if client.admin.command('ping')['ok'] == 1 else 1)"
  do
    echo "Waiting for MongoDB connection at ${host}:${port}..."
    sleep $RETRY_INTERVAL
    RETRIES=$((RETRIES+1))
    if [ $RETRIES -ge $MAX_RETRIES ]; then
      echo "MongoDB did not become ready in time, exiting..."
      exit 1
    fi
  done
  echo "MongoDB is up and running at ${host}:${port}"
}

check_mongo 'mongodb.jenkins.svc.cluster.local' 27017
check_mongo 'mongodb-test.jenkins.svc.cluster.local' 27018