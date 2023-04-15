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
cloud_URI = "https://coursework1-dd1g19.azurewebsites.net/api/prompt/edit?code=0Pp4ScvdFf8r1dWJHs_MQyQQZwwNQ-JLuRNyO2fUcH-lAzFuYRNUog=="
local_URI = 'http://localhost:7071/api/prompt/edit'
use_URI = cloud_URI # Change variable to local/cloud depending on use case

class TestFunction(unittest.TestCase):

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)

    def setUp(self) -> None:
        pass

    def test_edit_pass(self):
        # find amount of players before creating new one
        orig_prompts = list(self.prompts_container.read_all_items())

        payload = {"id": 1011732057318133, "text": "Prompt exists but matches current ID!", "username" : "Editer" , "password": "password123"}
        # tests if another user can create a prompt with the same text
        payload2 = {"id": 390741711748137, "text": "Text updated successfully!", "username" : "Editer" , "password": "password123"}
        payload3 = {"id": 390741711748137, "text": "Text updated to something different successfully!", "username" : "Editer" , "password": "password123"}

        resp = requests.get(use_URI, json = payload)
        resp2 = requests.get(use_URI, json = payload2)
        resp3 = requests.get(use_URI, json = payload3)
        
        # get new player account after registering
        prompts = list(self.prompts_container.read_all_items())
        
        # prompt count should not increase as only editing and not creating new prompts
        self.assertEqual(resp.json(), {"result" : True, "msg": "OK" })
        self.assertEqual(resp2.json(), {"result" : True, "msg": "OK" })
        self.assertEqual(resp3.json(), {"result" : True, "msg": "OK" })
        self.assertEqual(len(prompts),len(orig_prompts))

    def test_edit_fail(self):

        orig_prompts = list(self.prompts_container.read_all_items())
        
        payloadWrongId = {"id": 1, "text": "ID does not exist in container!", "username" : "Editer" , "password": "password123"}
        payloadWrongUser = {"id": 1087322230738505, "text": "Username does not exist in container", "username": "failUser" , "password": "Create1234"}
        payloadWrongPass = {"id": 1087322230738505, "text": "Password does not work!", "username": "Editer" , "password": "failPassword"}
        payloadTooShort = {"id": 1087322230738505, "text": "1234567890123456789", "username": "Editer" , "password": "password123"}
        payloadTooLong = {"id": 1087322230738505, "text": "This text is 101 characters long. qwertyuiopQWERTYUIOPasdfghjklASDFGHJKLzxcvbnmZXCVBNM123456789012345", 
            "username": "Editer" , "password": "password123"}
        payloadEmpty = {"id": 1087322230738505, "text": "", "username": "Editer" , "password": "password123"}
        payloadExists = {"id": 1011732057318133, "text": "Prompt already exists and id does not match!", "username": "Editer" , "password": "password123"}
        
        
        respWrongId = requests.get(use_URI, json = payloadWrongId)
        respExists = requests.get(use_URI, json = payloadExists)
        respWrongUser = requests.get(use_URI, json = payloadWrongUser)
        respWrongPass = requests.get(use_URI, json = payloadWrongPass)
        respWrongTooShort = requests.get(use_URI, json = payloadTooShort)
        respWrongTooLong = requests.get(use_URI, json = payloadTooLong)
        respEmpty = requests.get(use_URI, json = payloadEmpty)

        prompts = list(self.prompts_container.read_all_items())

        # prompt count should not have changed as no new prompts made
        self.assertEqual(respWrongId.json(), {"result": False, "msg": "prompt id does not exist" })
        self.assertEqual(respWrongUser.json(), {"result": False, "msg": "bad username or password" })
        self.assertEqual(respWrongPass.json(), {"result": False, "msg": "bad username or password" })
        self.assertEqual(respWrongTooShort.json(), {"result": False, "msg": "prompt length is <20 or >100 characters" })
        self.assertEqual(respWrongTooLong.json(), {"result": False, "msg": "prompt length is <20 or >100 characters" })
        self.assertEqual(respEmpty.json(), {"result": False, "msg": "prompt length is <20 or >100 characters" })
        self.assertEqual(respExists.json(), {"result": False, "msg": "This user already has a prompt with the same text" })
        self.assertEqual(len(prompts),len(orig_prompts))

