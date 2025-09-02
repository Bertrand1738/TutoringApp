import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Now try importing from models
from courses.models import Course, Video, PDF
print("Successfully imported Course, Video, PDF")

# Try to import Quiz directly
try:
    from courses.models import Quiz
    print("Quiz found in courses.models")
except ImportError as e:
    print(f"Error importing Quiz: {e}")

# Check all module attributes
print("\nAll attributes in courses.models:")
import courses.models
print(dir(courses.models))

# Now try importing the permission
print("\nTrying to import permissions:")
try:
    from core.permissions import IsEnrolledOrTeacher
    print("Import successful! IsEnrolledOrTeacher is properly defined.")
except ImportError as e:
    print(f"Import error: {e}")

# Print all available permissions in core.permissions
print("\nListing all classes in core.permissions:")
import core.permissions
for name in dir(core.permissions):
    obj = getattr(core.permissions, name)
    if isinstance(obj, type):  # Check if it's a class
        print(f" - {name}")
