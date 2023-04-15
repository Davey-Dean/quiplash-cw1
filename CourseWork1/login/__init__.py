import json
import logging
from operator import contains
from typing import Container

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
from requests import request
import os

db_URI = os.environ['db_URI']
db_id = os.environ['db_id']
db_key = os.environ['db_key']
players_cont = os.environ['players_container']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Attempting Login...')

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    login_req = req.get_json()

    #login_req["id"] = login_req.pop("username")

    id = login_req["username"]
    password = login_req["password"]

    try:
        query_result = list(players_container.query_items(
            query = "SELECT d FROM d WHERE d.id = @id AND d.password = @password", 
            parameters=[
                {"name" : "@id", "value" : id},
                {"name" : "@password", "value" : password}], 
            enable_cross_partition_query=True
        ))
        # if no queries returned then user/password combination does not exist
        if len(query_result) == 0:
            return func.HttpResponse(body=json.dumps({"result": False , "msg": "Username or password incorrect"}),status_code=200)
        elif len(query_result) == 1:
            return func.HttpResponse(body=json.dumps({"result": True , "msg" : "OK"}),status_code=200)
               
    except Exception as e:
        logging.info('something went wrong') 
