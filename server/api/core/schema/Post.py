import graphene
from graphene_django import types
from core.models import Post
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.translation import gettext as _
from graphql.error import GraphQLLocatedError

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
                Q(user__followers__in=[info.context.user], privacy='FOL')
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
                    Q(user__followers__in=[info.context.user], privacy='FOL'),
                )
            else:
                return Post.objects.get(
                    privacy='PUB',
                    pk=kwargs['pk']
                )
        except Post.DoesNotExist:
            raise Exception(_('Postagem não encontrada'))