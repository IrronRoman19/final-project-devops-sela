#!/bin/bash

until python -c "import sys; from pymongo import MongoClient; client = MongoClient('mongodb.jenkins.svc.cluster.local', 27017); sys.exit(0 if client.admin.command('ping')['ok'] == 1 else 1)"
do
  echo "Waiting for MongoDB connection at mongodb.jenkins.svc.cluster.local:27017..."
  sleep 5
done
echo "MongoDB is up and running at mongodb.jenkins.svc.cluster.local:27017"