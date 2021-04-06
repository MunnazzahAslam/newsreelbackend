# Generated by Django 3.1.5 on 2021-03-01 14:14

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0015_auto_20210215_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='voters',
            field=models.ManyToManyField(related_name='choice_voters', to=settings.AUTH_USER_MODEL),
        ),
    ]