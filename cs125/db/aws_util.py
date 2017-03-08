import boto3
import config
import uuid
import inspect
import models
from models import *
from cassandra.cqlengine import columns
from boto3.dynamodb import types
from boto3.dynamodb.conditions import Key, Attr
from boto3.exceptions import Boto3Error
from concurrent.futures import ThreadPoolExecutor
import log

logger = log.get_logger(__name__)

MAX_BATCH_SIZE = 1200

''' Convertion dict from cassandra model to aws '''
__columns_convert = {
    None : 'NULL',
    columns.Text: types.STRING,
    columns.Integer: types.NUMBER,
    columns.Decimal: types.NUMBER,
    columns.DateTime: types.STRING,
    columns.TimeUUID: types.STRING,
    columns.UUID: types.STRING,
    columns.Boolean: types.BOOLEAN,
    columns.Map: types.MAP
}

__HASH = 'HASH'
__RANGE = 'RANGE'
A_NAME = 'AttributeName'
I_NAME = 'IndexName'
P_NAME = 'Projection'
KS_NAME = 'KeySchema'
A_TYPE = 'AttributeType'
K_TYPE = 'KeyType'
P_TYPE = 'ProjectionType'

dynamodb = None
tables = {}



def setup():
    global dynamodb
    
    #dynamodb = boto3.resource('dynamodb', region_name=config.aws_region)
    dynamodb = boto3.resource('dynamodb')
    executor = ThreadPoolExecutor(max_workers=3)
    futures = []

    for module, _ in inspect.getmembers(models, inspect.ismodule):
        for name, model in inspect.getmembers(models.__dict__[module], inspect.isclass):
            if not model.__dict__.get('__ignore__', False) and issubclass(model, models.json_model.JsonModel):
                logger.info("Syncing table %s", name)
                keys, indices, attrs = __parse_class_to_dynamo(model)
                # Create tables
                futures.append(executor.submit(__create_table, model.__table_name__, keys, indices, attrs))
    while(len(futures) > 0):
        for table_future in list(futures):
            if table_future.done():
                table = table_future.result()
                assert not table is None
                name = table._name
                tables[name] = table
                futures.remove(table_future)
                logger.info("Table %s successfully processed!", name)
    logger.info("All tables successfully processed!")

                
def get_table(name):
    return tables[name]

def __get_dynamo_type(cass_type):
    '''
    :returns dynamo db type
    :params
        cass_type: cassandra type
    '''
    dynamo_type = __columns_convert[type(cass_type)]
    logger.debug("Type for %s is %s", cass_type, dynamo_type)
    return dynamo_type

def __get_python_object(obj):
    '''
    :returns python obj
    :params
        obj Cassandra object
    '''
    if type(obj) is uuid.UUID:
        return str(obj)

    else:
        return obj

def __get_columns_types(columns):
    '''
    For each column in column,
    :returns {column name : dynamodb type}
    :params
        columns: dict {column name, cassandra type}
    '''
    result = {}
    for col in columns:
        result[col] = __get_dynamo_type(columns[col])
    return result


def __parse_class_to_dynamo(cls):
    '''
    Parses the class to a general dynamodb json
    :returns tuple(keys, indices, attrs)
    see https://github.com/boto/boto3/blob/develop/docs/source/guide/dynamodb.rst
    '''
    if (not inspect.isclass(cls)):
        raise ValueError("cls must be a class")
    cass_cols = cls.__dict__['_columns']
    dynamo_types = __get_columns_types(cass_cols)
    keys = []
    indices = []
    attrs = []
    primary_key_count = 0
    for col in cass_cols:
        if cass_cols[col].primary_key:
            keys.append({A_NAME: col, K_TYPE: __HASH if primary_key_count == 0 else __RANGE})
            primary_key_count += 1
        elif cass_cols[col].partition_key:
            keys.append({A_NAME: col, K_TYPE: __RANGE})
        #elif cass_cols[col].index:
         #   indices.append({I_NAME: col, 
          #     KS_NAME: [{A_NAME: col, K_TYPE: __RANGE}], 
           #   P_NAME: {P_TYPE: 'KEYS_ONLY'}})
        else:
            continue #Non key attrs aren't needed for table creation
        attrs.append({A_NAME: col, A_TYPE: dynamo_types[col]})

    return keys, indices, attrs


def __parse_object_to_dynamo(obj):
    '''
    Parses the object to a general dynamodb json
    :returns items dict
    '''
    cols = obj.__dict__['_values']
    items = {}
    for v in cols:
        val = cols[v].getval()
        items[v] = __get_python_object(val)
    return items

def parse_to_dynamo_query(objs):
    for key in objs:
        return Key(key).eq(__get_python_object(objs[key]))

def parse_to_dynamo_scan(objs):
    conditions = None
    for key in objs:
        if conditions is None:
            conditions = Key(key).eq(objs[key])
        else:
            conditions = conditions & Key(key).eq(objs[key])
    return conditions
    
def parse_to_dynamo_write(obj):
    items = __parse_object_to_dynamo(obj)
    return items

def __parse_model():
    pass

def __create_table(name, keys, indices, attrs):
    '''
    Creates a new dynamo db table or returns the existing one
    see https://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table
    '''
    global dynamodb

    table = dynamodb.Table(name)
    try:
        table.load()
        logger.info("Found existing table for %s", name)
        return table
    except Exception as e:
        logger.debug("Table %s not found.", name)

    logger.debug("Creating table %s", name)
    table = dynamodb.create_table(
            TableName=name,
            KeySchema=keys,
            LocalSecondaryIndexes=indices,
            AttributeDefinitions=attrs,
           ProvisionedThroughput=config.dynamo_throughput
    ) if len(indices) > 0 else \
    dynamodb.create_table(
            TableName=name,
            KeySchema=keys,
            AttributeDefinitions=attrs,
           ProvisionedThroughput=config.dynamo_throughput
    )
                       
    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=name)

    # Print out some data about the table.
    return table 

if __name__ == '__main__':
    setup()
