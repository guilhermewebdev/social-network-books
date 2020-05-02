from graphene.test import format_execution_result, default_format_error
from graphql_jwt.testcases import JSONWebTokenTestCase, JSONWebTokenClient
from promise import Promise, is_thenable
from json import loads, dumps

class MyClient(JSONWebTokenClient):

    def __init__(self, format_error=None, **defaults):
        self.format_error = format_error or default_format_error
        super().__init__(**defaults)

    def format_result(self, result):
        return format_execution_result(result, self.format_error)
    
    def execute(self, query, variables=None, **extra): 
        executed = super().execute(query, variables=variables, **extra)
        if is_thenable(executed):
            return Promise.resolve(executed).then(self.format_result)
        return dict(loads(dumps(self.format_result(executed))))

class MyTestCase(JSONWebTokenTestCase):
    client_class = MyClient