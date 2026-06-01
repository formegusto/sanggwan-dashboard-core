import json
import pymysql

from pymongo import MongoClient

def get_local():
    with open("./auth.json", "r") as f:
        auth = json.load(f)["local"]
        uri = f'mongodb://{auth["username"]}:{auth["password"]}@{auth["host"]}:{auth["port"]}/{auth["database"]}'
        conn = MongoClient(uri)[auth["database"]]
    return conn

def get_remote():
    with open("./auth.json", "r") as f:
        auth = json.load(f)["remote"]
        conn = pymysql.connect(
            host=auth["host"], port=auth["port"], user=auth["username"], password=auth["password"],
            database=auth["database"], charset=auth["charset"], cursorclass=pymysql.cursors.DictCursor
       )
    return conn