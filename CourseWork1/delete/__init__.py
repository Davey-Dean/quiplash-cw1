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
prompts_cont = os.environ['prompts_container']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Deleting a prompt')
    
    # create proxy containers
    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)
    prompts_container = db_client.get_container_client(prompts_cont)

    # read input
    delete_req = req.get_json()

    user_name = delete_req["username"]
    user_password = delete_req["password"]
    prompt_id = str(delete_req["id"]) # int

    # perform query to check if user AND password exists in db
    query_players_result = list(players_container.query_items(
        query = "SELECT d FROM d WHERE d.id = @id AND d.password = @password", 
        parameters=[
            {"name" : "@id", "value" : user_name},
            {"name" : "@password", "value" : user_password}], 
        enable_cross_partition_query=True
    ))
    # if no user exists return error
    if len(query_players_result) == 0:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password" }),status_code=200)

    try:
        # check id exists in database
        prompt_data = prompts_container.read_item(item=prompt_id,partition_key=prompt_id)
        # check username attached to prompt is the same as the input username, if not throw error
        if prompt_data["username"] != user_name:
            return func.HttpResponse(body=json.dumps({"result": False, "msg": "access denied" }),status_code=200)
        else:
        # attempt to delete prompt from database
            prompts_container.delete_item(item=prompt_id,partition_key=prompt_id)
            return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }))
    except:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "prompt id does not exist" }),status_code=200)
