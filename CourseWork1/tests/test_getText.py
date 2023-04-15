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
cloud_URI = "https://coursework1-dd1g19.azurewebsites.net/api/prompts/getText?code=0Pp4ScvdFf8r1dWJHs_MQyQQZwwNQ-JLuRNyO2fUcH-lAzFuYRNUog==&clientId=default"
local_URI = 'http://localhost:7071/api/prompts/getText'
use_URI = cloud_URI # Change variable to test locally or 

class TestFunction(unittest.TestCase):

    client = cosmos.cosmos_client.CosmosClient(db_URI, db_key)
    db_client = client.get_database_client(db_id)
    prompts_container = db_client.get_container_client(prompts_cont)

    def setUp(self) -> None:
        pass

    def test_getText_prompts(self):

        prompts = [{"id": 1161430336551350 , "text" : "What Program you would never code in JavaScript", "username": "score1"},
                    {"id": 644817793903882 , "text" : "How many lines your shorter program has?", "username": "score3"}]
        
        payloadZero = {"word" : "program" , "exact" : True}
        respZero = requests.get(use_URI, json = payloadZero)
        self.assertEqual(respZero.json(), [{"id": 644817793903882 , "text" : "How many lines your shorter program has?", "username": "score3"}])

        payloadOne = {"word" : "program" , "exact" : False}
        respOne = requests.get(use_URI, json = payloadOne)
        sort_input = sorted(respOne.json(), key=lambda d: d['id'])
        sort_prompts = sorted(prompts, key=lambda d: d['id'])
        self.assertEqual(sort_input, sort_prompts)

        payloadNoMatch = {"word" : "NOMATCHINDB" , "exact" : False}
        respNoMatch = requests.get(use_URI, json = payloadNoMatch)
        self.assertEqual(respNoMatch.json(), [])
        payloadNoMatch2 = {"word" : "NOMATCHINDB" , "exact" : True}
        respNoMatch2 = requests.get(use_URI, json = payloadNoMatch2)
        self.assertEqual(respNoMatch2.json(), [])
        
        payloadEmpty = {"word" : "" , "exact" : True}
        respEmpty = requests.get(use_URI, json = payloadEmpty)
        self.assertEqual(respEmpty.json(), [])

    def test_getText_score4(self):
        
        prompts = [{"id": 739496890830755 , "text" : "testing for punctuation", "username": "score4"},
                    {"id": 160402017936075 , "text" : "testing for punctuation!?", "username": "score4"},
                    {"id": 108050303681554 , "text" : "testing for punctuation!!!!!", "username": "score4"},
                    {"id": 226924291703983 , "text" : "testing for punctuation. Another one", "username": "score4"},
                    {"id": 374070179127595 , "text" : "testing for punctuation.Another One", "username": "score4"},
                    {"id": 1027809303770025 , "text" : "testing for punctuation,word", "username": "score4"},
                    {"id": 472774358042693 , "text" : "testing for punctuation........another one", "username": "score4"},
                    {"id": 735199257516766 , "text" : "testing for punctuation!;;;;:::!!!?,.,.,.another one", "username": "score4"}]

        payloadZero = {"word" : "punctuation" , "exact" : True}
        respZero = requests.get(use_URI, json = payloadZero)
        sort_input = sorted(respZero.json(), key=lambda d: d['id'])
        sort_prompts = sorted(prompts, key=lambda d: d['id'])
        print(sort_input)
        print(sort_prompts)
        self.assertEqual(sort_input, sort_prompts)