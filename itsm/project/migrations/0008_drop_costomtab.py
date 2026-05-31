# Generated migration: drop CostomTab model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0007_costomtab"),
    ]

    operations = [
        migrations.DeleteModel(name="CostomTab"),
    ]
