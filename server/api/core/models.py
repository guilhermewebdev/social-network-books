from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model

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
        choices=BOOKSHELFS,
        verbose_name=_('Estado'),
    )
    favorite = models.BooleanField(
        verbose_name=_('Favorito'),
        default=False,
    )

    class Meta:
        verbose_name = _('Livro')
        verbose_name_plural = _('Livros')