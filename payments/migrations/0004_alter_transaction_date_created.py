# Generated by Django 4.1.7 on 2023-04-01 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_alter_transaction_callback_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='date_created',
            field=models.DateField(auto_now_add=True),
        ),
    ]
