import config
from .json_model import JsonModel
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

class Report(JsonModel):
    __table_name__ = "reports"
    id = columns.TimeUUID(primary_key=True)
    time = columns.DateTime(primary_key=True, clustering_order="DESC")
    location  = columns.Text(index=True)
    data = columns.Text()

    def hash(self):
        return '%s:%s' % (self.__table_name, self.id)

class Message(JsonModel):
    __table_name__ = "messages"
    address  = columns.Text(primary_key=True)
    message_index = columns.Integer(primary_key=True, clustering_order="DESC")
    subject = columns.Text()
    body = columns.Text()
    size = columns.Integer()
    sender = columns.Text()

    def hash(self):
        return '%s:%s:%s' % (self.__table_name, self.address, self.message_index)

