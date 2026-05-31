# Generated migration: drop deprecated WorkflowSnap and DefaultField models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("workflow", "0052_alter_state_type"),
    ]

    operations = [
        migrations.DeleteModel(name="WorkflowSnap"),
        migrations.DeleteModel(name="DefaultField"),
    ]
