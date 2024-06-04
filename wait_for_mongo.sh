#!/bin/bash
until nc -z -v -w30 $MONGO_DB_HOST $MONGO_DB_PORT
do
  echo "Waiting for MongoDB connection at $MONGO_DB_HOST:$MONGO_DB_PORT..."
  sleep 5
done
echo "MongoDB is up and running at $MONGO_DB_HOST:$MONGO_DB_PORT"