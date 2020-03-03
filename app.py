from flask import Flask, request, jsonify, g
import random, sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.config["DEBUG"] = True

DATABASE = "database.db"


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
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

# Read post data from a generated service endpoint
# If method is GET, retrieve the data from the database
# Else, if POST, store the data in the database
@app.route('/api/v1/resources/endpoint', methods=['GET', 'POST'])
def uri_endpoint ():
    query_parameters = request.args
    endpoint_id = query_parameters.get('id', type=int)
    if get_endpoint(endpoint_id):
        if request.method == 'GET':
            post_data = query_db('select post_data from highspot_app where endpoint_id = ?', (endpoint_id,), one=True)
            return jsonify({'post_data': post_data })
        elif request.method == 'POST':
            data = str(request.get_data(parse_form_data=False))
            query_db('update highspot_app set post_data = ? where endpoint_id = ?', (data, endpoint_id))
            db = get_db()
            db.commit()
            return jsonify({
                'request': data
                }), 201
    else:
        return ("Endpoint not found", 404)


# Generates a service endpoint that can store POST data to the database
@app.route('/api/v1/resources/endpoint/gen', methods=['GET'])
def generate_uri():
    value = random.randint(1000,9999)
    uri = "/api/v1/resources/endpoint?id=" + str(value) # construct the URI
    
    query_db('INSERT INTO highspot_app (endpoint_id) VALUES (?)', (value,))
    db = get_db()
    db.commit()
    return jsonify({ 'uri': uri })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port = 8080)