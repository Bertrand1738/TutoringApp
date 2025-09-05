from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    """
    Migration to add assignment model
    """
    dependencies = [
        ('courses', '0002_pdf_model'),
    ]

    operations = []
