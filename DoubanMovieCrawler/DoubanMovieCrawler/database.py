import pymongo

MONGO_HOST = '****'
MONGO_PORT = 27017

mongo_client = pymongo.MongoClient(f'mongodb://{MONGO_HOST}:{MONGO_PORT}')
db = mongo_client['douban']
col = db['movie']
