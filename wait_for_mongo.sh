#!/bin/bash

while ! python -c "
import sys
from pymongo import MongoClient
try:
    client = MongoClient('mongodb.jenkins.svc.cluster.local', 27017)
    client.admin.command('ping')
    sys.exit(0)
except Exception as e:
    print(f'Error connecting to MongoDB: {e}')
    sys.exit(1)
"; do
    echo "Waiting for MongoDB connection at mongodb.jenkins.svc.cluster.local:27017..."
    sleep 5
done
echo "MongoDB is up and running at mongodb.jenkins.svc.cluster.local:27017"