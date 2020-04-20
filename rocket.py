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

#Create a function to check the validity of the JWT token
def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
                #Create the token variable
                token = request.args.get('token')
                if not token:
                        return jsonify({'message' : 'please provide token'}),401
                #function to test validity of the jwt token. If incorrect return unauthorized access code 401
                try:
                        data  = jwt.decode(token, app.config['SECRET_KEY'])
                except:
                        return jsonify({'message' : 'Token is invalid'}),401
                return f(*args, **kwargs)
        return decorated
#Initial approach to website asks for user login and prompts user to input the token in the URL 
@app.route('/')
def login():
        auth = request.authorization
        if auth and auth.username == 'Test' and  auth.password =='password':
                        #Defining the arguments in the jwt.encode() with the token payload (username and password)
                token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=15)},app.config['SECRET_KEY'])
                #Provided that correct username input, display the token and url 
                return jsonify({'Please input the following token in the URL path' :'/rocket?token=' + token.decode('UTF-8')})
        #Deny access to path if incorrect credentials provided
        else:
        #Returns a 401 error for Unauthorized access error
                return make_response('Could not verify',{'WWW-Authenticate' : 'Basic realm="Login required"'},401)

@app.route('/rocket',methods=['GET'])
#View decorator to require user to have entered token for authorisation to this path
@token_required
def profile():
        rows = session.execute( """Select * from rocket.info""")
        result=[]
        for r in rows:
                result.append({"rocket_id":r.rocket_id,"boosters":r.boosters,"company":r.company,"cost_per_launch":r.cost_per_launch,"country":r.country,"engine_propellant":r.engine_propellant,"second_stage_pay_load":r.second_stage_pay_load,"type":r.type})
                return jsonify(result)

#External access to Web API which does not require login for access
@app.route('/<rocket>', methods=['GET'])
def get_rocket_external(rocket):
        rocket_url_template='https://api.spacexdata.com/v3/{rockets}'
        resp = requests.get(rocket_url_template.format(rockets = rocket))
        if resp.ok:
                rocket = resp.json()
                return jsonify(rocket),200
        else:
                print(resp.reason)

#Post method to create new rockets. All values need to be included in the Curl request to generate a valid 201 response
@app.route('/rocket',methods=['POST'])
def create_rocket():
        session.execute("""INSERT INTO rocket.info(rocket_id,boosters,company,cost_per_launch,country,engine_propellant,second_stage_pay_load,type) VALUES('{}',{},'{}',{},'{}','{}','{}','{}')""".format(request.json['rocket_id'],request.json['boosters'],request.json['company'],int(request.json['cost_per_launch']),request.json['country'],request.json['engine_propellant'],request.json['second_stage_pay_load'],request.json['type']))
        return jsonify({'message': 'created: /rocket/{}'.format(request.json['rocket_id'])}),201

#Put method which requires input of all fields except the cost_per_launch, company, engine propellant and type which remain consistent for each rocket
@app.route('/rocket',methods=['PUT'])
def update_rocket():
        session.execute("""UPDATE rocket.info SET boosters={},second_stage_pay_load='{}',country='{}' WHERE rocket_id ='{}'""".format(int(request.json['boosters']),request.json['second_stage_pay_load'],request.json['Country'],request.json['rocket_id']))
        return jsonify({'message': 'updated: /rocket/{}'.format(request.json['rocket_id'])}),200
#Delete method allows user to delete a full entry in the table using solely the rocket_id
@app.route('/rocket',methods=['DELETE'])
def delete_rocket():
        session.execute("""DELETE FROM rocket.info WHERE rocket_id='{}'""".format(request.json['rocket_id']))
        return jsonify({'message': 'Deleted: /rocket/{}'.format(request.json['rocket_id'])}),200
if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
