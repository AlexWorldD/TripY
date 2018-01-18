from pymongo import MongoClient
from pprint import pprint
from bson.json_util import dumps

client = MongoClient('mongodb://159.65.24.67')  # change the ip and port to your mongo database's
db = client.test
# serverStatusResult = db.command("serverStatus")
# pprint(serverStatusResult)
post = db.test
# post.insert_one({'status': 404, "create_time": 0})


# DUMP data from MongoDB
# print(dumps(db.test.find({})))
