# Generated by Django 5.2 on 2025-04-20 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0007_alter_booking_email_alter_booking_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='synopsis',
            field=models.TextField(blank=True, null=True),
        ),
    ]
