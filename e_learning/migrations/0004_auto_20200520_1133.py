# Generated by Django 3.0.5 on 2020-05-20 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_learning', '0003_auto_20200504_0913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjects_overview',
            name='duration',
            field=models.DurationField(help_text='[DD] [HH:[MM:]]ss[.uuuuuu] format---- eg 30 0:0'),
        ),
        migrations.AlterField(
            model_name='subjects_overview',
            name='video',
            field=models.FileField(blank=True, default='comingsoon_overview.mp4', null=True, upload_to=''),
        ),
    ]
