# Generated by Django 3.1.5 on 2021-02-12 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20210212_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='video_type',
            field=models.CharField(blank=True, choices=[('vimeo', 'Vimeo'), ('youtube', 'Youtube')], max_length=10, null=True),
        ),
    ]
