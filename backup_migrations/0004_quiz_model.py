from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_assignment_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('order_index', models.PositiveIntegerField(default=1)),
                ('is_preview', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('time_limit_minutes', models.PositiveIntegerField(default=30, help_text='Time limit in minutes (minimum 1 minute)')),
                ('passing_score', models.PositiveIntegerField(default=70, help_text='Minimum score required to pass (0-100)')),
                ('max_attempts', models.PositiveIntegerField(default=3, help_text='Maximum number of attempts allowed (minimum 1)')),
                ('questions', models.JSONField(default=list, help_text='Quiz questions in JSON format')),
                ('course', models.ForeignKey(on_delete=models.CASCADE, related_name='quizzes', to='courses.course')),
            ],
            options={
                'verbose_name': 'Quiz',
                'verbose_name_plural': 'Quizzes',
                'ordering': ['order_index'],
                'abstract': False,
            },
        ),
    ]
