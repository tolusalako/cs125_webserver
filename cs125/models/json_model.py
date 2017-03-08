from cassandra.cqlengine import models

class Model(models.Model):
    ''' Base Model Class '''
    __ignore__ = True
    __abstract__ = True


class DynamodbModel():
    __ignore__ = True
    __abstract__ = True


class JsonModel(Model):
    __abstract__ = True
    __ignore__ = True

    def toJson(self):
        keys = self.__dict__['_values'].keys()
        result = {}
        for key in keys:
            if key[0] != '_':
                result[key] = getattr(self, key, None)

        return result

