# Generated by Django 2.2.13 on 2020-09-13 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyse', '0005_photo_task_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='photo_link',
            field=models.TextField(max_length=1000, null=True, verbose_name='Photo link'),
        ),
    ]
