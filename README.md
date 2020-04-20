# Cloud
## Purpose of this Rest API
This REST API is a prototype cloud computing application developed in Python and Flask. It interacts with the SpaceX API to bring you information on their 4 rocket launches. It displays both the information on the external API and allows for various requests to be made to a dynamic REST API where entries can be posted, deleted, put and gotten from a Cassandra Database. 

### Accessing the Database
When you first access the website using the URL http://ec2.......com:5000/ you will be prompted to input a username and password. You can access the default settings by entering the username 'Test' and password 'password'. Upon doing this, you will be redirected to a page that will provide you a token for the session in JSON format. This needs to be input into the URL ?token='sessiontoken'. This will then give you access to view the information specific to the Cassandra database.
If an incorrect password is provided, access will be denied and authentication will fail producing a 401 response message. 

### Get Method for external API 
The information in the external API can be accessed using the URL http://ec2.........com:5000/rockets

### Functions and Requests
This REST API allows you to perform actions in order to implement changes to a Cassandra database using the following curl requests from a Terminal.

### Get Request 
Example request
curl -i -H "Content-Type: application/json" -X Get -d '{}'  http://ec2...com:5000/rockets
### Post Method
  Example request
curl -i -H "Content-Type: application/json" -X Post -d '{"rocket_id":"Falcon 1","engine_propellant":"liquid oxygen","boosters":"0","second_stage_pay_load":"Composite Fairing","cost_per_launch":6700000,"country":"Republic of Marshall Islands","company":"SpaceX","type":"rocket"}' http://ec2...com:5000/rocket
If this request is successful, a 201 response code will be returned.
### Put Method
  Example request
curl -i -H "Content-Type: application/json" -X Put -d '{"rocket_id":"Starship","boosters":0,"second_stage_pay_load":"Merlin","country":"United States"}' http://ec2...com:5000/rocket
If this request is successful, a 200 response code will be returned.
## Delete Method
  Example request
curl -i -H "Content-Type: application/json" -X Delete -d '{"rocket_id":"Falcon9"}'http://ec2.........com:5000/rocket
If this request is successful, a 200 response code will be returned.

## Cassandra DB Table Creation commands
CREATE KEYSPACE rocket WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 1};

CREATE TABLE rocket.info(rocket_id text PRIMARY KEY, Company text, cost_per_launch int, type text);

alter table rocket.info add second_stage_pay_load text,engine_propellant text,country text, boosters int;
