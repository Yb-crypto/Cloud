from flask import Flask, render_template, request, jsonify, make_response,redirect,url_for
from cassandra.cluster import Cluster
from datetime import date
import jwt
import datetime
import json
import requests
import csv
from functools import wraps

cluster = Cluster(contact_points=['127.0.0.1'],port=9042)
session = cluster.connect()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'rocket'

def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
                token = request.args.get('token')
                if not token:
                        return jsonify({'message' : 'token is missing'}),401

                try:
                        data  = jwt.decode(token, app.config['SECRET_KEY'])
                except:
                        return jsonify({'message' : 'Token is invalid'}),401
                return f(*args, **kwargs)
        return decorated

@app.route('/')
def login():
        auth = request.authorization
        if auth and auth.password =='password':
                token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=15)},app.config['SECRET_KEY'])
                return redirect(url_for('profile')+'?token=token')
        else:
                return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required"'})

@app.route('/rocket',methods=['GET'])
@token_required
def profile():
        rows = session.execute( """Select * from rocket.info""")
        result=[]
        for r in rows:
                result.append({"rocket_id":r.rocket_id,"company":r.company,"cost_per_launch":r.cost_per_launch,"type":r.type})
        return jsonify(result)

@app.route('/<rocket>', methods=['GET'])
def get_rocket_external(rocket):
    rocket_url_template='https://api.spacexdata.com/v3/{rockets}'
    resp = requests.get(rocket_url_template.format(rockets = rocket))
    if resp.ok:
        rocket = resp.json()
        return jsonify(rocket)
    else:
        print(resp.reason)
#@app.route('/rocket', methods=['POST'])
#def add_rocket():
#    rocket_url_template='https://api.spacexdata.com/v3/rockets/{rocket_id}'
#    resp = requests.get(rocket_url_template.format(rocket_id = request.json['rocket']))
#    if resp.ok:
#        rocket = resp.json()
#        return jsonify(rocket)
#    else:
#        print(resp.reason)

@app.route('/rocket',methods=['POST'])
def create_rocket():
        session.execute("""INSERT INTO rocket.info(rocket_id,company,cost_per_launch,type) VALUES('{}','{}',{},'{}')""".format(request.json['rocket_id'],request.json['company'],int(request.json['cost_per_launch']),request.json['type']))        
        return jsonify({'message': 'created: /rocket/{}'.format(request.json['rocket_id'])}),201
@app.route('/rocket',methods=['PUT'])
def update_rocket():
        session.execute("""UPDATE rocket.info SET type = '{}' WHERE rocket_id ='{}'""".format(request.json['rocket_id'],request.json['type']))        
        return jsonify({'message': 'updated: /rocket/{}'.format(request.json['rocket_id'])}),200
@app.route('/rocket',methods=['DELETE'])
def delete_rocket():
        session.execute("""DELETE FROM rocket.info WHERE rocket_id='{}'""".format(request.json['rocket_id']))
        return jsonify({'message': 'Deleted: /rocket/{}'.format(request.json['rocket_id'])}),200

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
