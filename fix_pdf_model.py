"""
Fixing the PDF model issue by directly adding to the module
"""
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("Adding the PDF class to the models module...")
try:
    # Import the module first
    import courses.models
    
    # Define the PDF class directly in the module namespace
    class PDFDocument(django.db.models.Model):
        """PDF document content"""
        course = django.db.models.ForeignKey('courses.Course', on_delete=django.db.models.CASCADE, related_name='pdfs')
        title = django.db.models.CharField(max_length=200)
        description = django.db.models.TextField(blank=True)
        order_index = django.db.models.PositiveIntegerField(default=1)
        is_preview = django.db.models.BooleanField(default=False)
        created_at = django.db.models.DateTimeField(auto_now_add=True)
        file = django.db.models.FileField(
            upload_to='course_pdfs/',
            help_text='Upload a PDF file (max 20MB)'
        )

        class Meta:
            app_label = 'courses'
            ordering = ["order_index"]
            verbose_name = "PDF"
            verbose_name_plural = "PDFs"

        def __str__(self):
            return f"{self.course.title} - {self.title}"
    
    # Add the class to the module
    courses.models.PDFDocument = PDFDocument
    
    # Add PDF alias
    courses.models.PDF = PDFDocument
    
    # Check if it worked
    print("Checking if the fix worked...")
    from courses.models import PDF, PDFDocument
    print(f"PDF class: {PDF}")
    print(f"PDFDocument class: {PDFDocument}")
    print("Fix successful!")
    
except Exception as e:
    print(f"Error fixing the model: {e}")
