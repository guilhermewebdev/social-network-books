import graphene
from graphene_django.debug import DjangoDebug
import graphql_jwt
from accounts import schema as accounts
from core import schema as core

class Query(
    graphene.ObjectType,
    accounts.Query,
    core.Query,
):
    debug = graphene.Field(DjangoDebug, name="_debug")

class Mutation(
    graphene.ObjectType,
    accounts.Mutation,
):
    debug = graphene.Field(DjangoDebug, name="_debug")
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    logout = graphql_jwt.Revoke.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)