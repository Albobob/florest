# Generated by Django 5.2 on 2025-05-01 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_telegramnotification_alter_order_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramnotification',
            name='first_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Имя'),
        ),
        migrations.AddField(
            model_name='telegramnotification',
            name='username',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Username'),
        ),
    ]
