"""
Migration to update model options, removing abstract=False from all content models
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_quiz_model'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ['order_index'], 'verbose_name': 'Video', 'verbose_name_plural': 'Videos'},
        ),
        migrations.AlterModelOptions(
            name='pdf',
            options={'ordering': ['order_index'], 'verbose_name': 'PDF', 'verbose_name_plural': 'PDFs'},
        ),
        migrations.AlterModelOptions(
            name='assignment',
            options={'ordering': ['order_index'], 'verbose_name': 'Assignment', 'verbose_name_plural': 'Assignments'},
        ),
        migrations.AlterModelOptions(
            name='quiz',
            options={'ordering': ['order_index'], 'verbose_name': 'Quiz', 'verbose_name_plural': 'Quizzes'},
        ),
    ]
