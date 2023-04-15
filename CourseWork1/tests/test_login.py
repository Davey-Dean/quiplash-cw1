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
cloud_URI = "https://coursework1-dd1g19.azurewebsites.net/api/player/login?code=0Pp4ScvdFf8r1dWJHs_MQyQQZwwNQ-JLuRNyO2fUcH-lAzFuYRNUog=="
local_URI = 'http://localhost:7071/api/player/login'
use_URI = cloud_URI # Change variable to test locally or

class TestFunction(unittest.TestCase):

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    def test_login_passes(self):

        payload = {"username": "testLogin" , "password" : "Login1234"}
        
        resp = requests.get(use_URI, json = payload)
                
        #print(resp.json())
        #players = list(self.players_container.read_all_items())
        #print(players)

        self.assertEqual(resp.json(), {"result" : True, "msg": "OK" })
        #the_tree_in_the_db = players[0]

    def test_login_fails(self):

        payloadWrongUser = {"username":  "TestLogin" , "password" : "Login1234"}
        payloadWrongPass = {"username":  "testLogin" , "password" : "login1234"}
        payloadWrongUserPass = {"username":  "TestLogin" , "password" : "login1234"}

        respWrongUser = requests.get(use_URI, json = payloadWrongUser)
        respWrongPass = requests.get(use_URI, json = payloadWrongPass)
        respWrongUserPass = requests.get(use_URI, json = payloadWrongUserPass)

        self.assertEqual(respWrongUser.json(), {"result": False , "msg": "Username or password incorrect"})
        self.assertEqual(respWrongPass.json(), {"result": False , "msg": "Username or password incorrect"})
        self.assertEqual(respWrongUserPass.json(), {"result": False , "msg": "Username or password incorrect"})



