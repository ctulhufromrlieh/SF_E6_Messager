# Generated by Django 4.2.7 on 2023-11-12 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_profile_selected_category_profile_selected_chat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='selected_category',
            field=models.IntegerField(default=-1),
        ),
    ]