# Generated by Django 3.0.5 on 2020-05-02 19:33

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20200502_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='bookshelf',
            field=models.CharField(max_length=3, verbose_name='Estado'),
        ),
        migrations.AlterField(
            model_name='post',
            name='privacy',
            field=models.CharField(max_length=3, verbose_name='Privacidade'),
        ),
        migrations.AlterField(
            model_name='reaction',
            name='reaction',
            field=models.CharField(max_length=2, validators=[core.models.ChoiceValidator((('LI', 'Gostei'), ('CI', 'Poderia melhorar'), ('FA', 'Fantástico')))], verbose_name='Reação'),
        ),
    ]