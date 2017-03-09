import config
from elasticsearch import Elasticsearch

es = None
index = config.elastic_search['index']

def setup():
    global es
    es = Elasticsearch([config.elastic_search['host']])
    print(index)
