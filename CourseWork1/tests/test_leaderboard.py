from http import client
import unittest
import json
import requests 

import azure.functions as func
import azure.cosmos as cosmos
import config


db_URI = config.settings['db_URI']
db_id = config.settings['db_id']
db_key = config.settings['db_key']
players_cont = config.settings['players_container']
cloud_URI = "https://coursework1-dd1g19.azurewebsites.net/api/player/leaderboard?code=0Pp4ScvdFf8r1dWJHs_MQyQQZwwNQ-JLuRNyO2fUcH-lAzFuYRNUog==&clientId=default"
local_URI = 'http://localhost:7071/api/player/leaderboard'
use_URI = cloud_URI # Change variable to test locally or 

class TestFunction(unittest.TestCase):

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    def setUp(self) -> None:
        # 
        pass

    def test_leaderboard(self):

        payload0 = {"top" : 1 }
        resp0 = requests.get(use_URI, json = payload0)
        self.assertEqual(resp0.json(), [{"username": "testUpdate" , "score": 25, "games_played":15}])

        payloadTop5 = {"top" : 5 }
        respTop5 = requests.get(use_URI, json = payloadTop5)
 
        # ensure alpha appears in list and not score7.
        self.assertEqual(respTop5.json(), [{"username": "testUpdate" , "score": 25, "games_played":15} ,  
                                        {"username": "score10", "score": 10, "games_played": 2},
                                        {"username": "score9", "score": 9, "games_played": 100},
                                        {"username": "score8", "score": 8, "games_played": 16},
                                        {"username": "alpha", "score": 7, "games_played": 0}])

        payloadTop6 = {"top" : 6 }
        respTop6 = requests.get(use_URI, json = payloadTop6)
 
        # ensure alpha is above score7 due to lexicographic ordering with ties
        self.assertEqual(respTop6.json(), [{"username": "testUpdate" , "score": 25, "games_played":15} ,  
                                        {"username": "score10", "score": 10, "games_played": 2},
                                        {"username": "score9", "score": 9, "games_played": 100},
                                        {"username": "score8", "score": 8, "games_played": 16},
                                        {"username": "alpha", "score": 7, "games_played": 0},
                                        {"username": "score7", "score": 7, "games_played": 7}])

        payloadTop1000 = {"top" : 1000 }
        respTop1000 = requests.get(use_URI, json = payloadTop1000)
 
        # not 1000 players in db, ensure all players appear
        self.assertEqual(respTop1000.json(), [{"username": "testUpdate" , "score": 25, "games_played":15} ,  
                                        {"username": "score10", "score": 10, "games_played": 2},
                                        {"username": "score9", "score": 9, "games_played": 100},
                                        {"username": "score8", "score": 8, "games_played": 16},
                                        {"username": "alpha", "score": 7, "games_played": 0},
                                        {"username": "score7", "score": 7, "games_played": 7},
                                        {"username": "score6", "score": 6, "games_played": 0},
                                        {"username": "score5", "score": 5, "games_played": 0},
                                        {"username": "score4", "score": 4, "games_played": 0},
                                        {"username": "score3", "score": 3, "games_played": 0},
                                        {"username": "aaaa", "score": 2, "games_played": 0},
                                        {"username": "aaaaa", "score": 2, "games_played": 0},
                                        {"username": "aaab", "score": 2, "games_played": 0},
                                        {"username": "baaa", "score": 2, "games_played": 0},
                                        {"username": "cccc", "score": 2, "games_played": 0},
                                        {"username": "score2", "score": 2, "games_played": 0},
                                        {"username": "score1", "score": 1, "games_played": 1000000},
                                        {"username": "Delete", "score": 0, "games_played": 0},
                                        {"username": "Editer", "score": 0, "games_played": 0},
                                        #{"username": "Wrapper", "score": 0, "games_played": 0},
                                        {"username": "testCreate", "score": 0, "games_played": 0},
                                        {"username": "testCreate2", "score": 0, "games_played": 0},
                                        {"username": "testLogin", "score": 0, "games_played": 0},
                                        {"username": "tester", "score": 0, "games_played": 0}])                                        
