from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

class User(AbstractUser):
    following = models.ManyToManyField(
        'accounts.User',
        related_name='followers',
    )

    class Meta:
        swappable = 'AUTH_USER_MODEL'
        abstract = False
        verbose_name = _('User')
        verbose_name_plural = _('Users')