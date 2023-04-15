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
    logging.info('Updating score and/or games played...')

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    update_req = req.get_json()

    user_id = update_req["username"]
    user_password = update_req["password"]

    # before query, check if user has inputted int <=0
    try:
        #check int's are not <= 0, otherwise return error msg
        if "add_to_score" in update_req:
            add_score = update_req["add_to_score"]
            if add_score <= 0:
               return func.HttpResponse(body=json.dumps({"result": False, "msg": "Value to add is <=0" }),status_code=200)
        if "add_to_games_played" in update_req:
            add_game = update_req["add_to_games_played"]
            if add_game <= 0:
                return func.HttpResponse(body=json.dumps({"result": False, "msg": "Value to add is <=0" }),status_code=200)
    
        # perform query to check user exists in db
        query_result = list(players_container.query_items(
            query = "SELECT * FROM d WHERE d.id = @id",
            parameters=[
                {"name" : "@id", "value" : user_id}],
            enable_cross_partition_query=True
        ))
        #print(json.dumps(query_result, indent=True))
        # if no user exists return error
        if len(query_result) == 0:
            return func.HttpResponse(body=json.dumps({"result": False, "msg": "user does not exist" }),status_code=200)
        # if user exists, check password matches
        else:
            for user in query_result:
                #print(json.dumps(user, indent=True))
                user_details = user
                if user["password"] != user_password:
                    return func.HttpResponse(body=json.dumps({"result": False, "msg": "wrong password" }),status_code=200)
        
        # grab relevant player from container
        #update_item = players_container.read_item(item = user_id, partition_key = user_id)

        # repeated code, could create a function or have the score checked after the query
        # update scores depending on input and return success message
        if "add_to_score" in update_req:
                user_details["total_score"] = user_details["total_score"] + add_score
        # use if and not elif as we want to check both score and games 
        if "add_to_games_played" in update_req:
                user_details["games_played"] = user_details["games_played"] + add_game
        # replace item in container once scores have been updated
        players_container.replace_item(item = user_details, body=user_details)
        return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),status_code=200)
    except Exception as e:
        logging.info('something went wrong') 
