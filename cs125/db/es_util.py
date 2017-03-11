import config
import uuid
from elasticsearch import Elasticsearch

es = None
index_name = config.elastic_search['index']


def getClient():
    global es
    # if es is None:
        # raise Exception("Elasticsearch was not initialized.")
    # else:
        # return es
    return es

def index(data):
    es.index(index=index_name, doc_type='tag', id=str(uuid.uuid1()), body=data)

def search(kw, val):
    return es.search(
        index=index_name,
        body={
            "query": {
                "match": {
                    kw: val
                }
            }
        });

def setup():
    global es
    es = Elasticsearch([config.elastic_search['host']])
    print(index_name)
