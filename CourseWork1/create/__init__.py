import json
import logging
from operator import contains
from typing import Container

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import os
import random

db_URI = os.environ['db_URI']
db_id = os.environ['db_id']
db_key = os.environ['db_key']
players_cont = os.environ['players_container']
prompts_cont = os.environ['prompts_container']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Creating new Prompt')

    # create proxy containers
    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)
    prompts_container = db_client.get_container_client(prompts_cont)

    # read input
    create_req = req.get_json()
    #print(json.dumps(list(create_req), indent=True))

    user_name = create_req["username"]
    user_password = create_req["password"]
    prompt_text = create_req["text"]

    # first check if prompt text is correct length
    if not 19 < len(prompt_text) < 101:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "prompt length is <20 or > 100 characters" }))

    # next perform query to check if user AND password exists in db
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

    # perform query on prompts container to check if user already has same text
    query_prompts_result = list(prompts_container.query_items(
        query = "SELECT p FROM p WHERE p.username = @username AND p.text = @text",
        parameters=[
            {"name" : "@username", "value" : user_name},
            {"name" : "@text", "value" : prompt_text}],
        enable_cross_partition_query=True
    ))
    # if a prompt exists throw error
    if len(query_prompts_result) != 0:
        return func.HttpResponse(body=json.dumps({"result": False, "msg": "This user already has a prompt with the same text" }),status_code=200)

    # generate random ID value for prompts
    unique_id = random.randint(0,1234567890123456)#78901234567890)
    # remove password from dictionary as we don't want to store that in prompts
    create_req.pop("password")
    # add new id to dictionary as a string
    create_req["id"] = str(unique_id)

    # Not the best way to generate a unique id, but assuming our databases are only working with a small amount of prompts (100's or 1000's)
    # then the likelyhood of genererating a preexisting id is extremely low
    # another method would be to read all prompts currently in database and find the largest id, then add one to that value.
    # Or store the largest ID as a value in the db and pull from it each time, but I thought both of these options would add to the load on 
    # the db.
    try:
        prompts_container.create_item(body=create_req)
        return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),status_code=200)
    except exceptions.CosmosHttpResponseError:
        # small chance for id to already be taken, reroll another random id and try to reassign.
        unique_id = random.randint(0,1234567890123456)
        prompts_container.create_item(body=create_req)
        return func.HttpResponse(body=json.dumps({"result" : True, "msg": "OK" }),status_code=200)
    
