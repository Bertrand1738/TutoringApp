from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_pdf_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('order_index', models.PositiveIntegerField(default=1)),
                ('is_preview', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('instructions', models.TextField(help_text='Detailed instructions for completing the assignment')),
                ('due_date', models.DateTimeField(blank=True, help_text='Optional deadline for submission (leave blank for no deadline)', null=True)),
                ('max_points', models.PositiveIntegerField(default=100, help_text='Maximum points possible for this assignment')),
                ('course', models.ForeignKey(on_delete=models.CASCADE, related_name='assignments', to='courses.course')),
            ],
            options={
                'verbose_name': 'Assignment',
                'verbose_name_plural': 'Assignments',
                'ordering': ['order_index'],
                'abstract': False,
            },
        ),
    ]
