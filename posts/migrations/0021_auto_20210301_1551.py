# Generated by Django 3.1.5 on 2021-03-01 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0020_auto_20210301_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.CharField(default='default_category', max_length=30),
            preserve_default=False,
        ),
    ]