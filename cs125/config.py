# Configuration file
import logging


host = "192.168.0.69"

elastic_search = {
    'host': '192.168.0.10',
    'index': 'cs125'
}



#======Controller============
workers = 1



#==========Versions============
versions = {
    'controller': 1.0,
}


#============logging===========
#Levels
log_levels = {
    'Sanic': logging.DEBUG,
    'sanic_cors': logging.DEBUG,
    'cassandra': logging.WARN,
    'RedisCache': logging.INFO,
}
