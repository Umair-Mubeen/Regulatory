# Generated by Django 5.0.6 on 2024-05-17 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FixApp', '0004_alter_orderevent_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderevent',
            name='TimeStamp',
            field=models.CharField(max_length=50),
        ),
    ]
