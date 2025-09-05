from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    """
    Migration to add quiz model
    """
    dependencies = [
        ('courses', '0003_assignment_model'),
    ]

    operations = []
