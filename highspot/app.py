from flask import Flask, request, jsonify, g
import random
import sqlite3
from sqlite3 import Error
from healthcheck import HealthCheck

app = Flask("highspot")
app.config["DEBUG"] = False
health = HealthCheck(app, "/healthcheck")  # Define healthcheck endpoint
DATABASE = "database.db"


# Function to get DB connection, returns the DB
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# SQLite3 DB healthcheck
def sqlite3_available():
    db = get_db()
    if db is not None:
        return True, "sqlite3 ok"
    else:
        return False, "sqlite3 not ok"


# Creates the DB and table if it doesn't already exist
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# Function to query database
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# Check if an endpoint exist
# Returns true, if exists, else returns false
def get_endpoint(endpoint_id):
    id = query_db('select * from highspot_app where endpoint_id = ?',
                [endpoint_id], one=True)
    if id is None:
        return False
    else:
        return True


# Home page
@app.route('/', methods=['GET'])
def home():
    return "<h1>Highspot API App</h1><p>Documentation: <a href=http://shorturl.at/lsTU8>http://shorturl.at/lsTU8</a></p>"


# Read post data from a generated service endpoint
# Must be content-type of application/json
# If method is GET, retrieve the data from the database
# Else, if POST, store the data in the database
@app.route('/api/v1/resources/endpoint', methods=['GET', 'POST'])
def uri_endpoint():
    query_parameters = request.args
    endpoint_id = query_parameters.get('id', type=int)
    if get_endpoint(endpoint_id):
        if request.method == 'GET':
            post_data = query_db('select post_data from highspot_app where endpoint_id = ?',
                                (endpoint_id,), one=True)
            return jsonify({'post_data': post_data})
        elif request.method == 'POST':
            if request.content_type != 'application/json':  # check content-type header, must be application/json!
                return jsonify({
                        'error': 'invalid content-type. must be application/json'
                    }), 415
            data = str(request.get_json())  # must cast the incoming data to string to store in the DB
            if query_db('update highspot_app set post_data = ? where endpoint_id = ?',
                    (data, endpoint_id)):
                db = get_db()
                db.commit()
                return jsonify({'request': data})
            else:
                return jsonify({'error': 'internal server error, could not save POST data to specified endpoint'}), 500
    else:
        return jsonify({
            'error': 'endpoint does not exist'
            }), 404


# Returns the latest submitted POST data from the database
@app.route('/api/v1/resources/endpoint/latest', methods=['GET'])
def get_latest():
    post_data = query_db('SELECT post_data FROM highspot_app WHERE post_data IS NOT NULL ORDER by post_timestamp DESC LIMIT 1', (), one=True)
    return jsonify({'post_data': post_data})


# Generates a service endpoint that can store POST data to the database
@app.route('/api/v1/resources/endpoint/gen', methods=['GET'])
def generate_uri():
    value = random.randint(1000, 9999)  # Random generated number that will service as the endpoint id
    uri = "/api/v1/resources/endpoint?id=" + str(value)  # construct the URI
    if query_db('INSERT INTO highspot_app (endpoint_id) VALUES (?)', (value,)):
        db = get_db()
        db.commit()
        return jsonify({'uri': uri}), 201
    else:
        return jsonify({'error': 'internal server error, could not create endpoint resource'}), 500


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
    health.add_check(sqlite3_available)
