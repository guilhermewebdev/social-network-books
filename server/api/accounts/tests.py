from django.test import TestCase
from graphene.test import Client
from api.schema import schema

class GraphqlTestCase(TestCase):
    
    def test_create_user(self):
        client = Client(schema)
        executed = client.execute('''
                mutation {
                    createUser(input: {
                        username: "teste"
                        firstName: "Teste"
                        lastName: "Teste"
                        email: "teste@teste.com"
                        password: "lfalkdf234"
                        terms: true
                    }){
                        user {
                            username
                        }
                    }
                }
        ''')
        assert 'errors' not in executed

    def test_users_list(self):
        client = Client(schema)
        executed = client.execute('''
            query {
                users {
                    username
                    firstName
                    lastName
                    pk
                }
            }
        ''')
        assert 'errors' not in executed
        assert 'data' in executed
        assert 'users' in executed['data'] and type(executed['data']['users']) == list
