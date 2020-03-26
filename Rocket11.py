from flask import Flask, render_template, request, jsonify
from cassandra.cluster import Cluster
import json
import requests
import csv
cluster = Cluster(contact_points=['127.0.0.1'],port=9042)
session = cluster.connect()

app = Flask(__name__)
from pprint import pprint

with open('rockets_db.csv') as rocket_db:
        csv_reader = csv.reader(rocket_db,delimiter=',')
        line_count=0

@app.route('/rocket',methods=['GET'])
def profile():
        rows = session.execute( """Select * from rocket.info""")
        result=[]
        for r in rows:
                result.append({"rocket_id":r.rocket_id,"company":r.company,"first_flight":r.first_flight,"active":r.active})
        return jsonify(result)

@app.route('/rocket/external', methods=['GET'])
def get_rocket(rocket):
    rocket_url_template='https://api.spacexdata.com/v3/rockets/{rocket_id}'
    resp = requests.get(rocket_url_template.format(rocket_id = rocket))
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
        session.execute("""INSERT INTO rocket.info(rocket_id,company,first_flight,active) VALUES('{}','{}',{},{})""".format(request.json['rocket_id'],request.json['company'],(date(request.json['first_flight'])),request.json['active']))
        return jsonify({'message': 'created: /rocket/{}'.format(request.json['rocket_id'])}),201
@app.route('/rocket',methods=['PUT'])
def update_rocket():
        session.execute("""UPDATE rocket.info SET active = '{}' WHERE rocket_id=[]""".format(request.json['rocket_id'],request.json['active']))
        return jsonify({'message': 'created: /rocket/{}'.format(request.json['rocket_id'])}),200
@app.route('/rocket',methods=['DELETE'])
def delete_rocket():    
        session.execute("""DELETE FROM rocket.info WHERE id={}""".format(request.json['rocket_id']))
        return jsonify({'message': 'Deleted: /rocket/{}'.format(request.json['id'])}),200
if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
