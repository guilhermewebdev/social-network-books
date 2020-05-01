from django.test import TestCase
from graphene.test import Client
from api.schema import schema
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase

class GraphqlTestCase(JSONWebTokenTestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create(username='test')
        self.client.authenticate(self.user)
    
    def test_create_user(self):
        self.client.execute('''
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

    def test_users_list(self):
        self.client.execute('''
            query {
                users {
                    username
                    firstName
                    lastName
                    pk
                }
            }
        ''')

    def test_update_user(self):
        self.client.execute('''
            mutation {
                updateUser(input: {
                    username: "tamandua"
                    firstName: "Tamaduá"
                })
            }
        ''')

    def test_delete_user(self):
        self.client.execute('''
            mutation {
                deleteUser(sure: true){
                    deleted
                }
            }
        ''')

    def test_me(self):
        self.client.execute('''
            query {
                me {
                    username
                    password
                    firstName
                }
            }
        ''')