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
    logging.info('Creating leaderboard...')

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)
    top_value = req.get_json().get("top")

    query_result = list(players_container.query_items(
            query = "SELECT TOP @k p.id AS username, p.total_score AS score, p.games_played FROM p ORDER BY p.total_score DESC, p.id ASC", 
            parameters=[
                {"name" : "@k", "value" : top_value}], 
            enable_cross_partition_query=True
    ))

    return func.HttpResponse(body=json.dumps(query_result), status_code=200)

    #print(json.dumps(query_result, indent=True))

    #------------ OLD CODE that didn't use query ------------#
    # grab all players from player container
    #all_players = list(players_container.read_all_items())

    # sorts players based on their total_score, ties are broken using their id's
    #sorted_players = sorted(all_players, key=lambda x: (-x['total_score'], x['id']))

    # takes top n players and adds them to list, only containing relevant information
    #top_players = []
    #for player in sorted_players[:top_value]:
    #    top_players.append({"username": player["id"] , "score": player["total_score"], "games_played":player["games_played"]})

    #print(json.dumps(top_players, indent=True))
    #----keeping incase something breaks with the query----#


