from graphene_django import types
import graphene
from django.utils.translation import gettext as _
from graphql import GraphQLError
from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required
from django.shortcuts import get_object_or_404, get_list_or_404
import graphql_jwt

User = get_user_model()

class UserType(types.DjangoObjectType):
    pk = graphene.ID()

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
            'pk',
            'followers'
        )

class UserQuery:
    users = graphene.List(UserType)
    user = graphene.Field(
        UserType,
        pk=graphene.ID(required=True)
    )
    me = graphene.Field(UserType)

    @staticmethod
    @login_required
    def resolve_user(parent, info, pk):
        return get_object_or_404(User, pk=pk)

    @staticmethod
    @login_required
    def resolve_users(parent, info, **kwargs):
        return User.objects.all().iterator()

    @staticmethod
    @login_required
    def resolve_me(parent, info):
        return info.context.user
    
class UserInputCreate(graphene.InputObjectType):
    username = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    terms = graphene.Boolean(required=True)

class UserMutationCreate(graphene.Mutation):
    user = graphene.Field(UserType)

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            user = User.objects.create_user(
                email=kwargs['input'].pop('email'),
                username=kwargs['input'].pop('username'),
                password=kwargs['input'].pop('password'),
            )
            for index in kwargs['input']:
                setattr(user, index, kwargs['input'][index])
            user.save()
            return UserMutationCreate(user=user)
        except:
            raise GraphQLError(_('Este usuário já está sendo utilizado'))   

    class Arguments:
        input = UserInputCreate(required=True)

class UserInputUpdate(graphene.InputObjectType):
    username = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    email = graphene.String()

class UserMutationUpdate(graphene.Mutation):
    user = graphene.Field(UserType)

    @staticmethod
    @login_required
    def mutate(root, info, **kwargs):
        try:
            user = info.context.user
            for (index, content) in kwargs['input']:
                setattr(user, index, content)
            user.save(update_fields=dir(kwargs['input']))
            return UserMutationUpdate(user=user)
        except:
            raise GraphQLError(_('Erro ao atualizar o usuário'))

    class Arguments:
        input = UserInputUpdate(required=True)

class UserMutationDeletion(graphene.Mutation):
    deleted = graphene.Boolean(required=True)

    @staticmethod
    @login_required
    def mutate(root, info, **kwargs):
        try:
            if(kwargs['sure'] == True):
                info.context.user.delete()
                return UserMutationDeletion(deleted=True)
            return UserMutationDeletion(deleted=False)
        except:
            raise GraphQLError(_('Não foi possível excluir o usuário'))

    class Arguments:
        sure = graphene.Boolean(required=True)

class UserMutation:
    create_user = UserMutationCreate.Field(
        description=_('User creation mutation')
    )
    update_user = UserMutationUpdate.Field(
        description=_('User update mutation')
    )
    delete_user = UserMutationDeletion.Field(
        description=_('User deletion mutation')
    )