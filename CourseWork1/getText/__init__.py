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
    logging.info('Fetching prompts containing word')
    
    # create proxy containers
    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)
    all_prompts = list(prompts_container.read_all_items())

    # read input
    get_req = req.get_json()
    word = req.get_json().get("word")

    # added cause "".join was causing matches on empty words
    if word == "":
        return func.HttpResponse(body=json.dumps([]))

    # function used to tidy prompts and get rid of data Azure adds
    def tidy_prompts(prompts):
        prompts_tidy = []
        for prompt in prompts:
            prompts_tidy.append({"id": int(prompt["id"]) , "text" : prompt["text"], "username": prompt["username"]})
        return prompts_tidy

    # function used to check if word exists in string, uses "exact" input to determine if exact case is to be checked
    def contains_word(prompt):
        #print(json.dumps((prompt), indent=True))
        punctuation = set(",.:;#\"-?!/")
        prompt = "".join([(x if x not in punctuation else " ") for x in prompt])
        if get_req["exact"]:
            return (' ' + word + ' ') in (' ' + prompt + ' ')
        else:
            return (' ' + word.lower() + ' ') in (' ' + prompt.lower() + ' ')

    # takes each prompt from the db and checks if the word exists
    word_prompts = []
    for prompt in all_prompts:
        if contains_word(prompt["text"]):
            word_prompts.append(prompt)
    word_prompts = tidy_prompts(word_prompts)
    return func.HttpResponse(body=json.dumps(word_prompts))

    #--------- OLD CODE --------#
    # # if exact == True...
    # if get_req["exact"]:
    #     # filter prompts that contain word (match case)
    #     word_prompts = []
    #     for prompt in all_prompts:
    #         if contains_word(prompt["text"]):
    #             word_prompts.append(prompt)
    #     word_prompts = tidy_prompts(word_prompts)
    #     return func.HttpResponse(body=json.dumps(word_prompts))
    # # else exact == False
    # else:
    #     # make both word and text lowercase, then compare and filter
    #     word_prompts = [x for x in all_prompts if word.lower() in x["text"].lower()]
    #     word_prompts = tidy_prompts(word_prompts)
    #     return func.HttpResponse(body=json.dumps(word_prompts))
