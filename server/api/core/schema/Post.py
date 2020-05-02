import graphene

from graphene_django import types

from graphql.error import GraphQLLocatedError

from core.models import Post

from graphene_file_upload.scalars import Upload

from graphql_jwt.decorators import login_required

from . import Comment

from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class PostNodeType(
    types.DjangoObjectType,
    Comment.Query,
):

    class Meta:
        model = Post
        fields = (
            'text',
            'date',
            'updated',
            'user',
            'image',
            'privacy',
            'comments',
        )
        interfaces = (graphene.Node,)

class PostConnection(graphene.Connection):
    count = graphene.Int()

    class Meta:
        node = PostNodeType

    def resolve_count(root, info):
        return len(root.edges)

class Query:
    posts = graphene.ConnectionField(PostConnection)
    post = graphene.Field(
        PostNodeType,
        pk=graphene.ID(required=True)
    )

    @staticmethod
    def resolve_posts(root, info, **kwargs):
        if info.context.user.is_authenticated:
            return list(Post.objects.filter(
                Q(user=info.context.user, privacy='PRI')|
                Q(
                    Q(user__followers__in=[info.context.user])|
                    Q(user=info.context.user),
                    Q(privacy='FOL')|Q(privacy='PUB')
                )
            ).order_by('-date').all().iterator())
        else:
            return Post.objects.filter(privacy='PUB').all()

    @staticmethod
    def resolve_post(root, info, **kwargs):
        try:
            if info.context.user.is_authenticated:
                return Post.objects.get(
                    Q(pk=kwargs['pk']),
                    Q(privacy='PUB')|
                    Q(user=info.context.user, privacy='PRI')|
                    Q(
                        Q(user__followers__in=[info.context.user])|
                        Q(user=info.context.user),
                        Q(privacy='FOL')
                    ),
                )
            else:
                return Post.objects.get(
                    privacy='PUB',
                    pk=kwargs['pk']
                )
        except Post.DoesNotExist:
            raise Exception(_('Postagem não encontrada'))

class PostCreationInput(graphene.InputObjectType):
    text = graphene.String(required=True)
    image = Upload()
    privacy = graphene.String(required=True)

class PostCreationMutation(graphene.Mutation):
    post = graphene.Field(PostNodeType)

    @login_required
    def mutate(root, info, **kwargs):
        try:
            post = Post(
                **kwargs['input'],
                user=info.context.user
            )
            post.full_clean()
            post.save()
            return PostCreationMutation(post=post)
        except ValidationError:
            raise Exception(_('Dados inválidos'))

    class Arguments:
        input = PostCreationInput(required=True)

class PostUpdateInput(graphene.InputObjectType):
    text = graphene.String()
    privacy = graphene.String()
    post = graphene.ID(required=True)

class PostUpdateMutation(graphene.Mutation):
    post = graphene.Field(PostNodeType)

    @login_required
    def mutate(root, info, **kwargs):
        try:
            post = Post.objects.get(
                pk=kwargs['input'].pop('post'),
                user=info.context.user
            )
            for index, value in kwargs['input'].items():
                setattr(post, index, value)
            post.full_clean()
            post.save(update_fields=list(kwargs['input']))
            return PostUpdateMutation(post=post)
        except Post.DoesNotExist:
            raise Exception(_('Postagem não encontrada'))
        except ValidationError:
            raise Exception(_('Dados Inválidos'))

    class Arguments:
        input = PostUpdateInput(required=True)

class PostDeletionMutation(graphene.Mutation):
    deleted = graphene.Boolean(required=True)

    def mutate(root, info, **kwargs):
        try:
            Post.objects.get(
                pk=kwargs['post'],
                user=info.context.user,
            ).delete()
            return PostDeletionMutation(deleted=True)
        except Post.DoesNotExist:
            raise Exception(_('Postagem não encontrada'))

    class Arguments:
        post = graphene.ID(required=True)

class Mutation:
    create_post = PostCreationMutation.Field()
    update_post = PostUpdateMutation.Field()
    delete_post = PostDeletionMutation.Field()