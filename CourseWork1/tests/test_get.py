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
prompts_cont = config.settings['prompts_container']
cloud_URI = "https://coursework1-dd1g19.azurewebsites.net/api/prompts/get?code=0Pp4ScvdFf8r1dWJHs_MQyQQZwwNQ-JLuRNyO2fUcH-lAzFuYRNUog==&clientId=default"
local_URI = 'http://localhost:7071/api/prompts/get'
use_URI = cloud_URI # Change variable to test locally or 

class TestFunction(unittest.TestCase):

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)

    def setUp(self) -> None:
        pass

    def test_get_prompts(self):

        num_of_prompts = len(list(self.prompts_container.read_all_items()))

        prompts = [{"id": 686977601838912, "text" : "prompt to be tested under delete section", "username": "tester"},
                    {"id": 825795337209967, "text" : "Text already exists!", "username": "testCreate"},
                    {"id": 1054274106221540, "text" : "Text already exists!", "username": "testCreate2"},
                    {"id": 1198478606005358, "text" : "12345678901234567890", "username": "testCreate"},
                    {"id": 1175938616221383, "text" : "12345678901234567890", "username": "testCreate2"},
                    {"id": 1087322230738505, "text" : "Prompt already exists and id does not match!", "username": "Editer"},
                    {"id": 1011732057318133, "text" : "Prompt exists but matches current ID!", "username": "Editer"},
                    {"id": 390741711748137, "text" : "Text updated to something different successfully!", "username": "Editer"},
                    {"id": 644817793903882, "text" : "How many lines your shorter program has?", "username": "score3"},
                    {"id": 377884308579448, "text" : "What is the funniest programming language?", "username": "score2"},
                    {"id": 1161430336551350, "text" : "What Program you would never code in JavaScript", "username": "score1"},
                    {"id": 1217116048367277, "text" : "This text is 100 characters long. qwerty uiop QWERTY UIOP asdfghjkl ASDFGHJKL zxcvbnm ZXCVBNM 123456",
                        "username": "testCreate2"},
                        {"id": 739496890830755 , "text" : "testing for punctuation", "username": "score4"},
                    {"id": 160402017936075 , "text" : "testing for punctuation!?", "username": "score4"},
                    {"id": 108050303681554 , "text" : "testing for punctuation!!!!!", "username": "score4"},
                    {"id": 226924291703983 , "text" : "testing for punctuation. Another one", "username": "score4"},
                    {"id": 374070179127595 , "text" : "testing for punctuation.Another One", "username": "score4"},
                    {"id": 1027809303770025 , "text" : "testing for punctuation,word", "username": "score4"},
                    {"id": 472774358042693 , "text" : "testing for punctuation........another one", "username": "score4"},
                    {"id": 735199257516766 , "text" : "testing for punctuation!;;;;:::!!!?,.,.,.another one", "username": "score4"}]

        sort_prompts = sorted(prompts, key=lambda d: d['id'])

        payloadZero = {"prompts" : 0}
        respZero = requests.get(use_URI, json = payloadZero)
         # input 0 should return empty list
        self.assertEqual(respZero.json(), [])

        payloadFive = {"prompts" : 5}
        respFive = requests.get(use_URI, json = payloadFive)
        len5 = len(respFive.json())
        self.assertEqual(len5,5)

        # test that all prompts are returned if n == number of prompts
        payloadAll = {"prompts" : num_of_prompts}
        respAll = requests.get(use_URI, json = payloadAll)
        lenAll = len(respAll.json())
        sort_input = sorted(respAll.json(), key=lambda d: d['id'])
        self.assertEqual(lenAll,num_of_prompts)
        self.assertEqual(sort_input, sort_prompts)

        # test that all prompts are returned if n > number of prompts
        payloadAll2 = {"prompts" : 10000}
        respAll2 = requests.get(use_URI, json = payloadAll2)
        lenAll2 = len(respAll2.json())
        sort_input2 = sorted(respAll2.json(), key=lambda d: d['id'])
        self.assertEqual(lenAll2,num_of_prompts)
        self.assertEqual(sort_input2, sort_prompts)

        self.assertEqual(respAll.json(),respAll2.json())

    def test_get_players(self):

        payloadZero = {"players" : []}
        respZero = requests.get(use_URI, json = payloadZero)
         # input 0 should return empty list
        self.assertEqual(respZero.json(), [])

        payloadFalse = {"players" : ["PLAYERDOESNOTEXIST"]}
        respFalse = requests.get(use_URI, json = payloadFalse)
         # input 0 should return empty list
        self.assertEqual(respFalse.json(), [])

        payloadOneP = {"players" : ["tester"]}
        respOneP = requests.get(use_URI, json = payloadOneP)
         # input 0 should return empty list
        self.assertEqual(respOneP.json(), [{"id": 686977601838912, "text" : "prompt to be tested under delete section", "username": "tester"}])

        payloadOPOF = {"players" : ["tester", "PLAYERDOESNOTEXIST"]}
        respOPOF = requests.get(use_URI, json = payloadOPOF)
         # input 0 should return empty list
        self.assertEqual(respOPOF.json(), [{"id": 686977601838912, "text" : "prompt to be tested under delete section", "username": "tester"}])

        payloadLots = {"players" : ["tester", "testCreate", "testCreate2"]}
        respLots = requests.get(use_URI, json = payloadLots)
        prompts = [{"id": 686977601838912, "text" : "prompt to be tested under delete section", "username": "tester"},
                    {"id": 825795337209967, "text" : "Text already exists!", "username": "testCreate"},
                    {"id": 1054274106221540, "text" : "Text already exists!", "username": "testCreate2"},
                    {"id": 1198478606005358, "text" : "12345678901234567890", "username": "testCreate"},
                    {"id": 1175938616221383, "text" : "12345678901234567890", "username": "testCreate2"},
                    {"id": 1217116048367277, "text" : "This text is 100 characters long. qwerty uiop QWERTY UIOP asdfghjkl ASDFGHJKL zxcvbnm ZXCVBNM 123456",
                        "username": "testCreate2"}]
        sort_prompts = sorted(prompts, key=lambda d: d['id'])
        sort_input = sorted(respLots.json(), key=lambda d: d['id'])
        self.assertEqual(sort_input, sort_prompts)
