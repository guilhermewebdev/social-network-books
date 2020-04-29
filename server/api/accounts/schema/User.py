from graphene_django import types
import graphene
from django.contrib.auth.models import User
from graphql_jwt.decorators import login_required
from django.shortcuts import get_object_or_404, get_list_or_404

class UserType(type.DjangoObjectType):

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'date_joined',
            'groups',
        )

class UserQuery:
    users = graphene.List(UserType)
    user = graphene.Field(
        UserType,
        pk=graphene.ID(required=True)
    )
    me = graphene.Field(UserType)

    @login_required
    def resolve_user(parent, info, pk):
        return get_object_or_404(User, pk=pk)

    @login_required
    def resolve_users(parent, info, **kwargs):
        return get_list_or_404(
            User
        )

    @login_required
    def resolve_me(parent, info):
        return info.context.user
    