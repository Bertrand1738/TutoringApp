"""
Test if the PDF model is working correctly
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Try to import the PDF model
from courses.models import PDF, Course

# Print confirmation
print("PDF model exists:", PDF is not None)

# Try to create a PDF instance
try:
    # First check if there are any courses
    courses = Course.objects.all()
    if courses.exists():
        course = courses.first()
        print(f"Found course: {course.title}")
        
        # Create a PDF instance (but don't save to database)
        pdf = PDF(
            course=course,
            title="Test PDF",
            description="This is a test PDF",
            file="test.pdf"
        )
        print("Successfully created PDF instance:", pdf)
        
        # Optionally save to database
        # pdf.save()
        # print("Successfully saved PDF to database")
    else:
        print("No courses found in database")
except Exception as e:
    print("Error creating PDF instance:", e)
