# Generated by Django 5.1.4 on 2024-12-08 22:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('llmanager', '0002_llmodel_llmprovider'),
    ]

    operations = [
        migrations.AlterField(
            model_name='llmproviderconfig',
            name='model',
            field=models.ForeignKey(help_text='The model that the AI will use to generate responses.', on_delete=django.db.models.deletion.CASCADE, to='llmanager.llmodel'),
        ),
        migrations.AlterField(
            model_name='llmproviderconfig',
            name='provider',
            field=models.ForeignKey(help_text='The provider that the AI will use to generate responses.', on_delete=django.db.models.deletion.CASCADE, to='llmanager.llmprovider'),
        ),
    ]
