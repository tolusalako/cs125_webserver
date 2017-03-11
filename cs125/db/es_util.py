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
    awsauth = AWS4Auth(config.aws['access_key'], config.aws['secret_key'], config.aws['region'], 'es')
    es = Elasticsearch(
        hosts=[{'host': config.elastic_search['host'], 'port': config.elastic_search['port']}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    print(index_name)
