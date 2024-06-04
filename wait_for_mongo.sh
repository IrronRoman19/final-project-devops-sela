#!/bin/bash

until python -c "import sys; from pymongo import MongoClient; client = MongoClient('$MONGO_DB_HOST', $MONGO_DB_PORT); sys.exit(0 if client.admin.command('ping')['ok'] == 1 else 1)"
do
  echo "Waiting for MongoDB connection at $MONGO_DB_HOST:$MONGO_DB_PORT..."
  sleep 5
done
echo "MongoDB is up and running at $MONGO_DB_HOST:$MONGO_DB_PORT"
