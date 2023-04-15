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
cloud_URI = "https://coursework1-dd1g19.azurewebsites.net/api/player/update?code=0Pp4ScvdFf8r1dWJHs_MQyQQZwwNQ-JLuRNyO2fUcH-lAzFuYRNUog==&clientId=default"
local_URI = 'http://localhost:7071/api/player/update'
use_URI = cloud_URI # Change variable to test locally or 

class TestFunction(unittest.TestCase):

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    def setUp(self) -> None:
        # setup resets user's score back to 0
        user = self.players_container.read_item(item = "testUpdate", partition_key = "testUpdate")
        user["total_score"] = 0
        user["games_played"] = 0
        self.players_container.replace_item(item = user, body=user)

    def test_update_passes(self):

        payloadScore = {"username": "testUpdate" , "add_to_games_played": 5, "password": "Update1234"}
        respScore = requests.get(use_URI, json = payloadScore)
        # check games after first update
        user = self.players_container.read_item(item = "testUpdate", partition_key = "testUpdate")
        self.assertEqual(user["games_played"], 5)
        self.assertEqual(user["total_score"], 0)

        payloadGame = {"username": "testUpdate" , "password": "Update1234" , "add_to_score" : 5 }
        respGame = requests.get(use_URI, json = payloadGame)
        # check score after first update
        user = self.players_container.read_item(item = "testUpdate", partition_key = "testUpdate")
        self.assertEqual(user["total_score"], 5)
        self.assertEqual(user["games_played"], 5)

        payloadScoreGame = {"username": "testUpdate" , "password": "Update1234" , "add_to_games_played" : 10 , "add_to_score" : 20 }
        respScoreGame = requests.get(use_URI, json = payloadScoreGame)
        # check games and score after second update
        user = self.players_container.read_item(item = "testUpdate", partition_key = "testUpdate")
        self.assertEqual(user["games_played"], 15)
        self.assertEqual(user["total_score"], 25)    

        # check msgs
        self.assertEqual(respScore.json(), {"result" : True, "msg": "OK" })
        self.assertEqual(respGame.json(), {"result" : True, "msg": "OK" })
        self.assertEqual(respScoreGame.json(), {"result" : True, "msg": "OK" })
    
    def test_update_fails_user(self):
        
        payloadWrongUser = {"username": "failUser" , "add_to_games_played": 1, "password": "Update1234"}
        payloadWrongPass = {"username": "testUpdate" , "add_to_games_played": 1, "password": "failPass"}

        respWrongUser = requests.get(use_URI, json = payloadWrongUser)
        respWrongPass = requests.get(use_URI, json = payloadWrongPass)

        self.assertEqual(respWrongUser.json(), {"result": False, "msg": "user does not exist" })
        self.assertEqual(respWrongPass.json(), {"result": False, "msg": "wrong password" })

    def test_update_fails_value(self):

        payloadWrongValue = {"username": "testUpdate" , "add_to_games_played": -50, "password": "Update1234"}
        payloadWrongValue2 = {"username": "testUpdate" , "password": "Update1234" , "add_to_score" : 0 }

        respWrongValue = requests.get(use_URI, json = payloadWrongValue)
        respWrongValue2 = requests.get(use_URI, json = payloadWrongValue2)

        self.assertEqual(respWrongValue.json(), {"result": False, "msg": "Value to add is <=0" })
        self.assertEqual(respWrongValue2.json(), {"result": False, "msg": "Value to add is <=0" })