CELERY_BROKER_URL = 'amqp://radmin:a@159.65.17.172:5672'
CELERY_RESULT_BACKEND = 'rpc://'
MONGO = 'mongodb://exam:A@159.65.17.172/TripY'
_DEV = False
_REVIEWS = True
_CONTACTS = False
# from config import *

from fake_useragent import UserAgent

ui = UserAgent()
