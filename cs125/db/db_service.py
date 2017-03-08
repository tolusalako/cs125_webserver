from models import model
from . import aws_util
import config
import inspect
import log
logger = log.get_logger(__name__)

if config.db is None:
    raise ValueError("Config.db cannot be null")

logger.info("Selected db is %s", config.db)

DYNAMO = 'dynamo'

def __class_check(object):
    if inspect.isclass(object) and issubclass(object, model.Model):
        return
    values = object.__dict__['_values']
    if not issubclass(type(object), model.Model)  or values is None:
        raise TypeError("%s is not a Model" % object)


def save(object):
    __class_check(object)

    table = aws_util.get_table(object.__table_name__)
    table.put_item(Item=aws_util.parse_to_dynamo_write(object))

def batch_save(objs):
    table = aws_util.get_table(objs[0].__table_name__)
    with table.batch_writer() as batch:
        for obj in objs:
            __class_check(obj)
            batch.put_item(Item=aws_util.parse_to_dynamo_write(obj))

def get(object, **kwargs):
    __class_check(object)
    
    table = aws_util.get_table(object.__table_name__)
    response = table.get_item(Key=kwargs)
    result = parse_object(object, response)
    return result

def query(object, **kwargs):
    __class_check(object)
    
    table = aws_util.get_table(object.__table_name__)
    print(aws_util.parse_to_dynamo_query(kwargs).__dict__)
    responses = table.query(KeyConditionExpression=aws_util.parse_to_dynamo_query(kwargs))
    result = parse_objects(object, responses)
    return result

def parse_objects(obj, json_values):
    #TODO
    print(json_values)
    2 + ''
    result = []


def parse_object(obj, json_values):
    print(json_values)
    attrs = json_values['Item']
    model = obj(**attrs)
    return model
