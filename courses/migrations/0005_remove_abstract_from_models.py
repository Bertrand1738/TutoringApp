from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    """
    Migration to remove abstract from models
    """
    dependencies = [
        ('courses', '0004_quiz_model'),
    ]

    operations = []
