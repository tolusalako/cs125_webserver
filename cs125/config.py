# Configuration file
import logging


'''
All times are in seconds
'''

#======Controller============
workers = 1

#============Cor==============
cor_origins = "*"
cor_methods = 'POST, GET'
cor_headers = 'Authorization, Content-Type'
cor_creds = 'true'
cor_max_age = '300'

#==========Versions============
versions = {
    'controller': 1.0,
}


#==========Databases===============
db = 'dynamodb'

# Dynamo DB
dynamo_throughput = {
    'ReadCapacityUnits': 5,
    'WriteCapacityUnits': 5
}


#============logging===========
#Levels
log_levels = {
    'Sanic': logging.DEBUG,
    'sanic_cors': logging.DEBUG,
    'cassandra': logging.WARN,
    'RedisCache': logging.INFO,
}
