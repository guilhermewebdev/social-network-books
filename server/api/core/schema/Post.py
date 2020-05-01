import graphene
from graphene_django import types
from core.models import Post
from django.shortcuts import get_object_or_404
from django.db.models import Q

class PostNodeType(types.DjangoObjectType):

    class Meta:
        model = Post
        fields = (
            'text',
            'date',
            'updated',
            'user',
            'image',
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
                Q(user__followers__in=[info.context.user], privacy='FOL'),
            ).all()
        else:
            return Post.objects.filter(privacy='PUB').all()

    @staticmethod
    def resolve_post(root, info, **kwargs):
        if info.context.user.is_authenticated:        
            return get_object_or_404(Post,
                Q(pk=kwargs['pk']),
                Q(privacy='PUB')|
                Q(user__followers__in=[info.context.user], privacy='FOL'),
            )
        else:
            return get_object_or_404(
                Post,
                privacy='PUB',
            )