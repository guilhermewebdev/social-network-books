from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

@deconstructible
class ChoiceValidator(object):
    def __init__(self, choices):
        self.choices = [a for (a, b) in choices]

    def __call__(self, value):
        if not value in self.choices:
            raise ValidationError(
                _('%(value) não é uma opção válida'),
                params={ 'value': value }
            )

class Book(models.Model):
    BOOKSHELFS = [
        ('TRE', _('Lido')),
        ('WTR', _('Gostaria de Ler')),
        ('HNR', _('Tem mas não leu')),
        ('RHT', _('Leu há muito tempo')),
        ('REN', _('Lendo atuamente')),
        ('ABD', _('Abandonou a leitura')),
    ]
    objects = models.Manager()
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name=_('Usuário'),
    )
    book = models.CharField(
        max_length=30,
        verbose_name=_('Livro'),
    )
    bookshelf = models.CharField(
        max_length=3,
        verbose_name=_('Estado'),
        validators=[ChoiceValidator(BOOKSHELFS)],
        choices=BOOKSHELFS,
    )
    favorite = models.BooleanField(
        verbose_name=_('Favorito'),
        default=False,
    )

    class Meta:
        verbose_name = _('Livro')
        verbose_name_plural = _('Livros')

class Post(models.Model):
    PERMISSIONS = (
        ('PUB', _('Público')),
        ('PRI', _('Privado')),
        ('FOL', _('Seguidores')),
    )
    text = models.TextField(
        verbose_name=_('Texto da postagem'),
        max_length=2000,
    )
    date = models.DateTimeField(
        verbose_name=_('Data da postagem'),
        auto_now=True,
    )
    updated = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Última atualização')
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('Dono da postagem'),
    )
    image = models.ImageField(
        verbose_name=_('Imagem'),
        upload_to='media/uploads/',
        null=True,
        blank=True,
    )
    privacy = models.CharField(
        max_length=3,
        validators=[ChoiceValidator(PERMISSIONS)],
        verbose_name=_('Privacidade'),
        choices=PERMISSIONS,
    )

    class Meta:
        verbose_name = _('Postagem')
        verbose_name_plural = _('Postagens')

class Comment(models.Model):
    text = models.TextField(
        verbose_name=_('Comentário'),
        max_length=1000,
    )
    date = models.DateTimeField(
        verbose_name=_('Data do comentário'),
        auto_now=True
    )
    updated = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Última atualização')
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Comentador'),
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name=_('Postagem'),
        related_name='comments'
    )

    class Meta:
        verbose_name = _('Comentário')
        verbose_name_plural = _('Comentários')

class Reaction(models.Model):
    REACTIONS = (
        ('LI', _('Gostei')),
        ('CI', _('Poderia melhorar')),
        ('FA', _('Fantástico')),
    )
    reaction = models.CharField(
        verbose_name=_('Reação'),
        max_length=2,
        validators=[ChoiceValidator(REACTIONS)],
        choices=REACTIONS,
    )
    date = models.DateTimeField(
        verbose_name=_('Data da reação'),
        auto_now=True
    )
    updated = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Última atualização')
    )

    class Meta:
        verbose_name = _('Reação')
        verbose_name_plural = _('Reações')

class PostReaction(Reaction):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name=_('Reações'),
        related_name='reactions'
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='post_reactions',
        verbose_name=_('Comentador'),
    )

    class Meta:
        unique_together = ('post', 'user')

class CommentReaction(Reaction):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        verbose_name=_('Reações'),
        related_name='reactions'
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='comment_reactions',
        verbose_name=_('Comentador'),
    )

    class Meta:
        unique_together = ('comment', 'user')