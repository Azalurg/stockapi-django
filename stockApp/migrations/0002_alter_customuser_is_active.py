# Generated by Django 5.0.2 on 2024-02-26 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stockApp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
