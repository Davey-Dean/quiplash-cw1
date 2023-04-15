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
cloud_URI = "https://coursework1-dd1g19.azurewebsites.net/api/prompt/create?code=0Pp4ScvdFf8r1dWJHs_MQyQQZwwNQ-JLuRNyO2fUcH-lAzFuYRNUog=="
local_URI = 'http://localhost:7071/api/prompt/create'
use_URI = cloud_URI # Change variable to local/cloud depending on use case

class TestFunction(unittest.TestCase):

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)

    def setUp(self) -> None:
        # setup deletes prompts with certain texts
        query_result = list(self.prompts_container.query_items(
            query = "SELECT * FROM d WHERE d.text = @text",
            parameters=[
                {"name" : "@text", "value" : "12345678901234567890"}],
            enable_cross_partition_query=True
        ))
        for item in query_result:
            delete_id = item["id"]
            try:
                self.prompts_container.delete_item(item = delete_id, partition_key = delete_id)
            except:
                pass

    def test_create_pass(self):

        # find amount of players before creating new one
        orig_prompts = list(self.prompts_container.read_all_items())

        payload = {"text": "12345678901234567890", "username": "testCreate" , "password": "Create1234"}
        # tests if another user can create a prompt with the same text
        payload2 = {"text": "12345678901234567890", "username": "testCreate2" , "password": "Create12345"}
        #payload100 = {"text": "This text is 100 characters long. qwerty uiop QWERTY UIOP asdfghjkl ASDFGHJKL zxcvbnm ZXCVBNM 123456",
                        #"username": "testCreate2" , "password": "Create12345"}

        resp = requests.get(use_URI, json = payload)
        resp2 = requests.get(use_URI, json = payload2)
        #resp100 = requests.get(use_URI, json = payload100)
        
        # get new player account after registering
        prompts = list(self.prompts_container.read_all_items())
        
        # prompt count should have increased by 2
        self.assertEqual(resp.json(), {"result" : True, "msg": "OK" })
        self.assertEqual(resp2.json(), {"result" : True, "msg": "OK" })
        #self.assertEqual(resp100.json(), {"result" : True, "msg": "OK" })
        self.assertEqual(len(prompts),len(orig_prompts) + 2)# + 3)

    def test_create_fail(self):

        orig_prompts = list(self.prompts_container.read_all_items())

        payloadExists = {"text": "Text already exists!", "username": "testCreate" , "password": "Create1234"}
        payloadWrongUser = {"text": "Username does not exist", "username": "failUser" , "password": "Create1234"}
        payloadWrongPass = {"text": "Password does not work!", "username": "testCreate" , "password": "failPassword"}
        payloadTooShort = {"text": "1234567890123456789", "username": "testCreate" , "password": "Create1234"}
        payloadTooLong = {"text": "This text is 101 characters long. qwertyuiopQWERTYUIOPasdfghjklASDFGHJKLzxcvbnmZXCVBNM123456789012345", 
            "username": "testCreate" , "password": "Create1234"}
        payloadEmpty = {"text": "", "username": "testCreate" , "password": "Create1234"}

        respExists = requests.get(use_URI, json = payloadExists)
        respWrongUser = requests.get(use_URI, json = payloadWrongUser)
        respWrongPass = requests.get(use_URI, json = payloadWrongPass)
        respWrongTooShort = requests.get(use_URI, json = payloadTooShort)
        respWrongTooLong = requests.get(use_URI, json = payloadTooLong)
        respEmpty = requests.get(use_URI, json = payloadEmpty)

        prompts = list(self.prompts_container.read_all_items())

        # player count should not have changed as no new prompts made
        self.assertEqual(respExists.json(), {"result": False, "msg": "This user already has a prompt with the same text" })
        self.assertEqual(respWrongUser.json(), {"result": False, "msg": "bad username or password" })
        self.assertEqual(respWrongPass.json(), {"result": False, "msg": "bad username or password" })
        self.assertEqual(respWrongTooShort.json(), {"result": False, "msg": "prompt length is <20 or > 100 characters" })
        self.assertEqual(respWrongTooLong.json(), {"result": False, "msg": "prompt length is <20 or > 100 characters" })
        self.assertEqual(respEmpty.json(), {"result": False, "msg": "prompt length is <20 or > 100 characters" })
        self.assertEqual(len(prompts),len(orig_prompts))

