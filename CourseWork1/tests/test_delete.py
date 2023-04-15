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
prompts_cont = config.settings['prompts_container']
cloud_URI = "https://coursework1-dd1g19.azurewebsites.net/api/prompt/delete?code=0Pp4ScvdFf8r1dWJHs_MQyQQZwwNQ-JLuRNyO2fUcH-lAzFuYRNUog=="
local_URI = 'http://localhost:7071/api/prompt/delete'
use_URI = cloud_URI # Change variable to local/cloud depending on use case

class TestFunction(unittest.TestCase):

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)

    def setUp(self) -> None:
        # create prompt to be deleted.
        item = self.prompts_container.read_item(item="1011732057318133",partition_key="1011732057318133")
        item["username"] = "Delete"
        item["id"] = "1234"
        try:
            self.prompts_container.create_item(body=item)
        except:
            pass

    def test_delete_pass(self):

        # find amount of players before creating new one
        orig_prompts = list(self.prompts_container.read_all_items())

        payload = {"id" : 1234, "username" : "Delete" , "password": "PromptRemoved"}
        # test to ensure correct prompt deleted
        payload2 = {"id" : 1234, "username" : "Delete" , "password": "PromptRemoved"}

        resp = requests.get(use_URI, json = payload)
        resp2 = requests.get(use_URI, json = payload2)
        
        # get new player account after registering
        prompts = list(self.prompts_container.read_all_items())
        
        # prompt count should have increased by 2
        self.assertEqual(resp.json(), {"result" : True, "msg": "OK" })
        self.assertEqual(resp2.json(), {"result": False, "msg": "prompt id does not exist" })
        self.assertEqual(len(prompts),len(orig_prompts) - 1)

    def test_delete_fail(self):

        orig_prompts = list(self.prompts_container.read_all_items())
        
        payloadWrongId = {"id": 1, "username" : "Delete" , "password": "PromptRemoved"}
        payloadWrongUser = {"id": 686977601838912, "username": "failUser" , "password": "PromptRemoved"}
        payloadWrongPass = {"id": 686977601838912, "username": "Delete" , "password": "failPassword"}
        payloadDenied = {"id": 686977601838912, "username": "Editer" , "password": "password123"}
        
        
        respWrongId = requests.get(use_URI, json = payloadWrongId)
        respWrongUser = requests.get(use_URI, json = payloadWrongUser)
        respWrongPass = requests.get(use_URI, json = payloadWrongPass)
        respDenied = requests.get(use_URI, json = payloadDenied)

        prompts = list(self.prompts_container.read_all_items())

        # prompt count should not have changed as no prompts deleted
        self.assertEqual(respWrongId.json(), {"result": False, "msg": "prompt id does not exist" })
        self.assertEqual(respWrongUser.json(), {"result": False, "msg": "bad username or password" })
        self.assertEqual(respWrongPass.json(), {"result": False, "msg": "bad username or password" })
        self.assertEqual(respDenied.json(), {"result": False, "msg": "access denied" })
        self.assertEqual(len(prompts),len(orig_prompts))
