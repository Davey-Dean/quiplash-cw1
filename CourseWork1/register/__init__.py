import json
import logging
from operator import contains
from typing import Container

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import os

db_URI = os.environ['db_URI']
db_id = os.environ['db_id']
db_key = os.environ['db_key']
players_cont = os.environ['players_container']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Registering new User.')

    # Create the needed proxy objects for CosmosDB account, database and tree container
    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)

    # Create a proxy object to the treehuggers Cosmos DB database
    db_client = client.get_database_client(db_id)

    # Create a proxy object to the trees container
    players_container = db_client.get_container_client(players_cont)

    player = req.get_json()

    if not 4 <= len(player["username"]) <= 16:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "Username less than 4 characters or more than 16 characters"}))
    elif not 8 <= len(player["password"]) <= 24:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "Password less than 8 characters or more than 24 characters"}))

    # convert username key to id, as database needs it that way
    player["id"] = player.pop("username")

    # add games played and total score to player 
    player["games_played"] = 0
    player["total_score"] = 0

    # attempt to create new item in database using player, if it doesn't work then the id already exists in the db
    try:
        players_container.create_item(body=player)
        return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),status_code=200)
    except exceptions.CosmosHttpResponseError:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "Username already exists" }),status_code=200)
    
