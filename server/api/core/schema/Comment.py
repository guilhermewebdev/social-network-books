import graphene

from graphene_django import types

from core.models import Comment, Post

from graphql_jwt.decorators import login_required

from django.utils.translation import gettext as _
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class CommentNodeType(types.DjangoObjectType):

    class Meta:
        model = Comment
        fields = (
           'text',
           'date',
           'updated',
           'user',
           'post',
        )
        interfaces = (graphene.Node,)

class CommentConnection(graphene.Connection):
    count = graphene.Int()

    class Meta:
        node = CommentNodeType

    def resolve_count(root, info):
        return len(root.edges)

class Query:
    comments = graphene.ConnectionField(CommentConnection)
    comment = graphene.Field(
        CommentNodeType,
        pk=graphene.ID(required=True)
    )

    @staticmethod
    def resolve_comments(parent, info):
        return list(parent.comments.order_by('-date').iterator())

    @staticmethod
    def resolve_comment(parent, info, pk):
        try:
            return parent.comments.get(pk=pk)
        except Comment.DoesNotExist:
            raise Exception(_('Comentário não encontrado'))

class ComentCreationInput(graphene.InputObjectType):
    text = graphene.String(required=True)
    post = graphene.ID(reqired=True)

class CommentCreationMutation(graphene.Mutation):
    comment = graphene.Field(CommentNodeType)

    def mutate(root, info, **kwargs):
        try:
            post = Post.objects.get(
                Q(pk=kwargs['input'].pop('post')),
                Q(privacy='PUB')|
                Q(user=info.context.user, privacy='PRI')|
                Q(
                    Q(user__followers__in=[info.context.user])|
                    Q(user=info.context.user),
                    Q(privacy='FOL')
                ),
            )
            comment = Comment(
                post=post,
                **kwargs['input'],
                user=info.context.user
            )
            comment.full_clean()
            comment.save()
            return CommentCreationMutation(comment=comment)
        except Post.DoesNotExist:
            raise Exception(_('Postagem não encontrada'))

    class Arguments:
        input = ComentCreationInput(required=True)

class Mutation:
    comment_post = CommentCreationMutation.Field()