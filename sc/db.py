from pymongo import MongoClient
from pprint import pprint
from bson.json_util import dumps

client = MongoClient('mongodb://exam:A@159.65.17.172/TripY')  # change the ip and port to your mongo database's
db = client.TripY
serverStatusResult = db.command("serverStatus")
pprint(serverStatusResult)
db.test.insert_one({'test': 1})
# post.insert_one({'status': 404, "create_time": 0})


# DUMP data from MongoDB
# print(dumps(db.test.find({})))
