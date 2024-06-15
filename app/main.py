from flask import Flask, render_template, request, redirect, url_for, g
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

def get_db():
    if 'db' not in g:
        mongo_db_name = 'task_db_test' if app.config['TESTING'] else 'task_db'
        mongo_db_user = os.getenv('MONGO_DB_USER', 'mongoadmin')
        mongo_db_pass = os.getenv('MONGO_DB_PASS', 'secret')
        mongo_db_host = os.getenv('MONGO_DB_HOST', 'task-db.default.svc.cluster.local')
        mongo_db_port = int(os.getenv('MONGO_DB_PORT', 27017))
        mongo_db_address = f'mongodb://{mongo_db_user}:{mongo_db_pass}@{mongo_db_host}:{mongo_db_port}/'
        client = MongoClient(mongo_db_address)
        g.db = client[mongo_db_name]
    return g.db

@app.before_request
def before_request():
    g.db = get_db()

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.client.close()

tasks_collection = lambda: g.db.tasks

@app.route('/count')
def count():
    count = tasks_collection().count_documents({})
    return str(count)

@app.route('/count_completed')
def count_completed():
    completed_count = tasks_collection().count_documents({'completed': True})
    return str(completed_count)

@app.route('/count_uncompleted')
def count_uncompleted():
    uncompleted_count = tasks_collection().count_documents({'completed': False})
    return str(uncompleted_count)

@app.route('/')
def home():
    tasks = list(tasks_collection().find().sort('destination', 1))
    task_count = tasks_collection().count_documents({})
    completed_count = tasks_collection().count_documents({'completed': True})
    uncompleted_count = tasks_collection().count_documents({'completed': False})
    return render_template('index.html', tasks=tasks, task_count=task_count, completed_count=completed_count, uncompleted_count=uncompleted_count, str=str)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        full_name = request.form['full_name']
        task_name = request.form['task_name']
        description = request.form['description']
        destination = request.form['destination']
        creation_date = datetime.utc().strftime('%d/%m/%Y %H:%M')

        destination_datetime = datetime.strptime(destination, '%Y-%m-%dT%H:%M')

        tasks_collection().insert_one({
            'full_name': full_name,
            'task_name': task_name,
            'description': description,
            'destination': destination_datetime,
            'creation_date': creation_date,
            'completed': False
        })
        
        return redirect(url_for('home'))
    return render_template('create.html', str=str)

@app.route('/delete/<task_id>')
def delete(task_id):
    tasks_collection().delete_one({'_id': ObjectId(task_id)})
    return redirect(url_for('home'))

@app.route('/edit/<task_id>', methods=['GET', 'POST'])
def edit(task_id):
    task = tasks_collection().find_one({'_id': ObjectId(task_id)})
    if request.method == 'POST':
        updated_task = {
            'full_name': request.form['full_name'],
            'task_name': request.form['task_name'],
            'description': request.form['description'],
            'destination': datetime.strptime(request.form['destination'], '%Y-%m-%dT%H:%M')
        }
        tasks_collection().update_one({'_id': ObjectId(task_id)}, {'$set': updated_task})
        return redirect(url_for('home'))
    # Format the date for the form
    task['destination'] = task['destination'].strftime('%Y-%m-%dT%H:%M')
    return render_template('edit.html', task=task, str=str)

@app.route('/complete/<task_id>')
def complete(task_id):
    tasks_collection().update_one({'_id': ObjectId(task_id)}, {'$set': {'completed': True}})
    return redirect(url_for('home'))

@app.route('/uncomplete/<task_id>')
def uncomplete(task_id):
    tasks_collection().update_one({'_id': ObjectId(task_id)}, {'$set': {'completed': False}})
    return redirect(url_for('home'))

def main():
    try:
        get_db().list_collection_names()
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Failed to connect to MongoDB:\n{e}")
    app.run(debug=True)

if __name__ == '__main__':
    main()