"""
Fix import issue with PDF model
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# We're going to define the model exactly as it should be in our models.py file
class PDF(models.Model):
    """PDF document content"""
    course = models.ForeignKey('courses.Course', related_name='pdfs', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order_index = models.PositiveIntegerField(default=1)
    is_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to='course_pdfs/',
        help_text='Upload a PDF file (max 20MB)'
    )

    class Meta:
        ordering = ["order_index"]
        verbose_name = "PDF"
        verbose_name_plural = "PDFs"

    def __str__(self):
        return f"{self.course.title} - {self.title}"
        
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.file:
            # Check file size (20MB limit)
            if self.file.size > 20 * 1024 * 1024:
                raise ValidationError({
                    'file': 'File size cannot exceed 20MB.'
                })
            
            # Check file extension
            if not self.file.name.lower().endswith('.pdf'):
                raise ValidationError({
                    'file': 'Only PDF files are allowed.'
                })
