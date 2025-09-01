from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial_content_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('order_index', models.PositiveIntegerField(default=1)),
                ('is_preview', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(help_text='Upload a PDF file (max 20MB)', upload_to='course_pdfs/')),
                ('course', models.ForeignKey(on_delete=models.CASCADE, related_name='pdfs', to='courses.course')),
            ],
            options={
                'verbose_name': 'PDF',
                'verbose_name_plural': 'PDFs',
                'ordering': ['order_index'],
                'abstract': False,
            },
        ),
    ]
