"""
Debugging the PDF model import with Django setup
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# First let's try importing directly
try:
    print("Trying direct import...")
    from courses.models import Video, PDF, Assignment, Quiz
    print("Success! Models imported.")
    print(f"PDF model: {PDF}")
except ImportError as e:
    print(f"Failed direct import: {e}")

# If that fails, try importing by fully qualifying the name
try:
    print("\nTrying fully qualified import...")
    from courses import models
    pdf_model = getattr(models, 'PDF', None)
    if pdf_model:
        print(f"Success! PDF model found via qualified import: {pdf_model}")
    else:
        print("PDF model not found in the models module.")
except Exception as e:
    print(f"Failed qualified import: {e}")

# Let's check what's available in the models module
try:
    print("\nListing all model classes in the models module:")
    import inspect
    import courses.models
    
    model_classes = []
    for name, obj in inspect.getmembers(courses.models):
        if inspect.isclass(obj) and issubclass(obj, django.db.models.Model) and obj != django.db.models.Model:
            model_classes.append(name)
            
    print(f"Available model classes: {model_classes}")
except Exception as e:
    print(f"Error listing models: {e}")

# Let's reload the module to ensure we have the latest version
try:
    print("\nTrying to reload the module:")
    import importlib
    importlib.reload(courses.models)
    print("Module reloaded!")
    
    # Check if PDF is available after reload
    pdf_model = getattr(courses.models, 'PDF', None)
    if pdf_model:
        print(f"PDF model found after reload: {pdf_model}")
    else:
        print("PDF model still not found after reload.")
except Exception as e:
    print(f"Error reloading module: {e}")
