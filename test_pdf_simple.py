"""
Very simple script to verify PDF model is working
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import models
from courses.models import PDF, Course

# Test PDF model
print("PDF model exists:", PDF is not None)

# Check for courses
course = Course.objects.first()
print("Found course:", course is not None if course else "No courses found in database")

# If a course exists, create a PDF object
if course:
    pdf = PDF(
        course=course,
        title='Test PDF',
        description='Test description',
        file='test.pdf'
    )
    print("PDF object created successfully")
    print(f"PDF object: {pdf}")
    
    # Try to save it
    try:
        pdf.save()
        print("PDF object saved to database successfully")
    except Exception as e:
        print(f"Error saving PDF: {e}")
