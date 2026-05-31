# Generated migration: drop deprecated OldSla, ServiceProperty, PropertyRecord models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("service", "0031_auto_20210621_1206"),
    ]

    operations = [
        migrations.DeleteModel(name="PropertyRecord"),
        migrations.DeleteModel(name="ServiceProperty"),
        migrations.DeleteModel(name="OldSla"),
    ]
