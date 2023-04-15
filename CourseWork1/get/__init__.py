import json
import logging
from operator import contains
from typing import Container

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import os
from random import sample

db_URI = os.environ['db_URI']
db_id = os.environ['db_id']
db_key = os.environ['db_key']
prompts_cont = os.environ['prompts_container']

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Fetching prompts')
    
    # create proxy containers
    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)
    all_prompts = list(prompts_container.read_all_items())

    # read input
    get_req = req.get_json()
    
    # function used to tidy prompts and get rid of data Azure adds
    def tidy_prompts(prompts):
        prompts_tidy = []
        for prompt in prompts:
            prompts_tidy.append({"id": int(prompt["id"]) , "text" : prompt["text"], "username": prompt["username"]})
        return prompts_tidy

    # check if input is "prompts" or "players"
    if "prompts" in get_req:
        n = get_req["prompts"]
        # if n is equal to or greater than the amount of prompts, then return all prompts
        if len(all_prompts) <= n:
            prompts = tidy_prompts(all_prompts)
            return func.HttpResponse(body=json.dumps(prompts))
        # else use random.sample to get a random n amount of prompts from the list
        else:
            n_prompts = sample(all_prompts,n)
            prompts = tidy_prompts(n_prompts)
            return func.HttpResponse(body=json.dumps(prompts))
    # use elif as it can only be "prompts" or "players" not both
    elif "players" in get_req:
        players = get_req["players"]
        user_prompts = [x for x in all_prompts if x["username"] in players]
        prompts = tidy_prompts(user_prompts)
        return func.HttpResponse(body=json.dumps(prompts))