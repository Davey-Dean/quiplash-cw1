#from http import client
import unittest
import json
import requests

import azure.functions as func
import azure.cosmos as cosmos
import config
#Important for the import name to match the case of the Function folder
#from register import main

db_URI = config.settings['db_URI']
db_id = config.settings['db_id']
db_key = config.settings['db_key']
players_cont = config.settings['players_container']
cloud_URI = "https://coursework1-dd1g19.azurewebsites.net/api/player/register?code=0Pp4ScvdFf8r1dWJHs_MQyQQZwwNQ-JLuRNyO2fUcH-lAzFuYRNUog==&clientId=default"
local_URI = 'http://localhost:7071/api/player/register'
use_URI = cloud_URI # Change variable to local/cloud depending on use case

class TestFunction(unittest.TestCase):

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    players_container = db_client.get_container_client(players_cont)

    def setUp(self) -> None:
        # setup deletes user "tester" if it exists, allowing for us to re-create and test
        try:
            self.players_container.delete_item(item = "tester", partition_key = "tester")
        except:
            pass

    def test_register_pass(self):

        # find amount of players before creating new one
        orig_players = list(self.players_container.read_all_items())

        payload = {"username":  "tester" , "password" : "test1234"}
        payloadRepeat = {"username":  "tester" , "password" : "test1234"}

        resp = requests.get(
                #This is the URL of the function deployed in the local development server
                # The URL of the Cloud deployment depends on the URL of the resource group
                use_URI, 
                #send payload as JSON
                json = payload)
        respRepeat = requests.get(use_URI, json = payloadRepeat)
        
        # get new player account after registering
        players = list(self.players_container.read_all_items())
        
        #print(resp.json())
        #print(players)

        # player count should have increased by
        self.assertEqual(resp.json(), {"result" : True, "msg": "OK" })
        self.assertEqual(respRepeat.json(), {"result": False, "msg": "Username already exists" })
        self.assertEqual(len(players),len(orig_players) + 1)
        

    def test_register_fail(self):

        orig_players = list(self.players_container.read_all_items())

        payloadExists = {"username":  "testLogin" , "password" : "test1234"}
        payloadWrongUserShort = {"username":  "tes" , "password" : "test1234"}
        payloadWrongUserLong = {"username":  "qwertyuiopasdfghj" , "password" : "test1234"}
        payloadWrongPassShort = {"username":  "tester1" , "password" : "test123"}
        payloadWrongPassLong = {"username":  "tester2" , "password" : "qwertyuiopasdfghjklzxcvbn"}

        respExists = requests.get(use_URI, json = payloadExists)
        respWrongUserShort = requests.get(use_URI, json = payloadWrongUserShort)
        respWrongUserLong = requests.get(use_URI, json = payloadWrongUserLong)
        respWrongPassShort = requests.get(use_URI, json = payloadWrongPassShort)
        respWrongPassLong = requests.get(use_URI, json = payloadWrongPassLong)

        players = list(self.players_container.read_all_items())

        # player count should not have changed as no new players made
        self.assertEqual(respExists.json(), {"result": False, "msg": "Username already exists" })
        self.assertEqual(respWrongUserShort.json(), {"result": False, "msg": "Username less than 4 characters or more than 16 characters"})
        self.assertEqual(respWrongUserLong.json(), {"result": False, "msg": "Username less than 4 characters or more than 16 characters"})
        self.assertEqual(respWrongPassShort.json(), {"result": False, "msg": "Password less than 8 characters or more than 24 characters"})
        self.assertEqual(respWrongPassLong.json(), {"result": False, "msg": "Password less than 8 characters or more than 24 characters"})
        self.assertEqual(len(players),len(orig_players))

