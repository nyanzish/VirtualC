# Generated by Django 3.0.5 on 2020-06-04 23:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('e_learning', '0009_comment_user_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatcomment',
            options={'ordering': ['created_on']},
        ),
    ]
