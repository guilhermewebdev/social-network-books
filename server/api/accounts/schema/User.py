from graphene_django import types
import graphene
from django.utils.translation import gettext as _
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required
from django.shortcuts import get_object_or_404, get_list_or_404
import graphql_jwt

User = get_user_model()

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
    
class UserInputCreate(graphene.InputObjectType):
    username = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)

class UserMutationCreate(graphene.Mutation):
    user = graphene.Field(UserType)

    @staticmethod
    @login_required
    def mutate(root, info, **kwargs):
        try:
            user = User.create_user(
                email=kwargs['input'].pop('email'),
                username=kwargs['input'].pop('username'),
                password=kwargs['input'].pop('password'),
            )
            for (index, content) in kwargs:
                setattr(user, index, content)
            user.save()
            return UserMutationCreate(user=user)
        except:
            raise GraphQLError(_('Este usuário já está sendo utilizado'))   

    class Arguments:
        input = UserInputCreate(required=True)