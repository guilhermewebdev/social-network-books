import graphene

from graphene_django import types

from graphql.error import GraphQLLocatedError

from core.models import Post

from graphene_file_upload.scalars import Upload

from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class PostNodeType(types.DjangoObjectType):

    class Meta:
        model = Post
        fields = (
            'text',
            'date',
            'updated',
            'user',
            'image',
            'privacy',
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
            return Post.objects.filter(
                Q(privacy='PUB')|
                Q(user=info.context.user, privacy='PRI')|
                Q(
                    Q(user__followers__in=[info.context.user])|
                    Q(user=info.context.user),
                    Q(privacy='FOL')
                )
            ).all()
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

class Mutation:
    create_post = PostCreationMutation.Field()