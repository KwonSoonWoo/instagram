# Generated by Django 2.0.7 on 2018-07-26 06:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20180702_0334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='_author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
    ]
