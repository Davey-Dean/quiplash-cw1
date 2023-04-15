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
    logging.info('Edit a Prompt...')

    # create proxy containers
    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)
    prompts_container = db_client.get_container_client(prompts_cont)

    # read input
    edit_req = req.get_json()
    #print(json.dumps(list(edit_req), indent=True))

    user_name = edit_req["username"]
    user_password = edit_req["password"]
    prompt_text = edit_req["text"]
    prompt_id = edit_req["id"] # int
    #print(json.dumps(((prompt_id)), indent=True))

    # check if prompt text is correct length
    if not 19 < len(prompt_text) < 101:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "prompt length is <20 or >100 characters" }))

    # perform query to check if user AND password exists in db
    query_players_result = list(players_container.query_items(
        query = "SELECT * FROM d WHERE d.id = @id AND d.password = @password", 
        parameters=[
            {"name" : "@id", "value" : user_name},
            {"name" : "@password", "value" : user_password}], 
        enable_cross_partition_query=True
    ))
    # if no user exists return error
    if len(query_players_result) == 0:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "bad username or password" }),status_code=200)

    # perform query on prompts container to check if user already has prompt with same text
    query_prompts_result = list(prompts_container.query_items(
        query = "SELECT * FROM p WHERE p.username = @username AND p.text = @text",
        parameters=[
            {"name" : "@username", "value" : user_name},
            {"name" : "@text", "value" : prompt_text}],
        enable_cross_partition_query=True
    ))
    # if a prompt exists, check if ID matches input ID
    # was told if edit text is same as current prompt, should return "OK"
    if len(query_prompts_result) != 0:
        for prompt in query_prompts_result:
            #print(json.dumps((prompt["id"]), indent=True))
            #print(json.dumps(((prompt_id)), indent=True))
            if prompt["id"] != str(prompt_id):
                return func.HttpResponse(body=json.dumps({"result": False, "msg": "This user already has a prompt with the same text" }),status_code=200)

    # attempt to grab prompt from container using id, not sure if this is more or less resource intense than queries
    try:
        update_prompt = prompts_container.read_item(item = str(prompt_id), partition_key = str(prompt_id))
    except:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "prompt id does not exist" }),status_code=200)
    # if prompt with id exists update text
    update_prompt["text"] = prompt_text
    # push update to container
    try:
        prompts_container.replace_item(item = update_prompt, body=update_prompt)
        return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),status_code=200)
    except Exception as e:
        logging.info('something went wrong') 
