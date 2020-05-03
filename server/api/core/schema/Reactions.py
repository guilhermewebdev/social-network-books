import graphene

from graphene_django import types

from graphql.error import GraphQLLocatedError

from core.models import PostReaction

from graphene_file_upload.scalars import Upload

from graphql_jwt.decorators import login_required

from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class PostReactionType(types.DjangoObjectType):
    amount = graphene.Int(
        required=True,
        reaction=graphene.String()
    )
    avaliables = graphene.List(graphene.String)

    def resolve_avaliables(parent, info):
        return [a for (a, b) in PostReaction.REACTIONS]

    def resolve_amount(parent, info, reaction):
        if reaction:
            return parent.reactions.filter(reaction=reaction).count()
        return parent.reactions.all().count()

    class Meta:
        model = PostReaction
        fields = (
            'reaction',
            'date',
            'updated',
            'user',
            'post',
            'amount',
            'avaliables',
        )

class Query:
    reactions = graphene.Field(PostReactionType)

    @staticmethod
    def resolve_reactions(parent, info):
        return parent.reactions.all()