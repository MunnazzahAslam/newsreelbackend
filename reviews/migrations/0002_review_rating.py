# Generated by Django 3.1.5 on 2021-01-18 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='rating',
            field=models.FloatField(blank=True, editable=False, null=True),
        ),
    ]
