"""
Directly fixing PDF model # Let's check what's available in the models module
try:
    print("\nListing all model classes in the models module:")
    import courses.models
    
    # Import the module directly
    import importlib.util
    import sys
    
    # Load the module directly from file
    module_path = 'courses/models.py'
    module_name = 'courses.models'
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    # Check if PDFDocument is in the fresh module
    if hasattr(module, 'PDFDocument'):
        print("PDFDocument found in freshly loaded module!")
    else:
        print("PDFDocument not found in freshly loaded module")
    
    # Check all models
    import inspect
    from django.db import models as django_models
    
    print("\nListing all model classes in the models module:")
    model_classes = []
    for name, obj in inspect.getmembers(courses.models):
        if inspect.isclass(obj) and issubclass(obj, django_models.Model) and obj != django_models.Model:
            model_classes.append(name)
    
    print(f"Available model classes: {model_classes}")
    
except Exception as e:
    print(f"Error listing attributes: {e}")

# Let's try inspecting the PDF model's sourceue
"""

# First let's try importing directly
try:
    print("Trying direct import...")
    from courses.models import PDF
    print("Success! PDF model imported.")
except ImportError as e:
    print(f"Failed direct import: {e}")

try:
    print("\nTrying to import PDFDocument...")
    from courses.models import PDFDocument
    print("Success! PDFDocument model imported.")
except ImportError as e:
    print(f"Failed PDFDocument import: {e}")

# If that fails, try importing by fully qualifying the name
try:
    print("\nTrying fully qualified import...")
    from courses import models
    pdf_model = getattr(models, 'PDF', None)
    if pdf_model:
        print("Success! PDF model found via qualified import.")
    else:
        print("PDF model not found in the models module.")
except Exception as e:
    print(f"Failed qualified import: {e}")

# Let's check what's available in the models module
try:
    print("\nListing all attributes in the models module:")
    import courses.models
    attrs = [attr for attr in dir(courses.models) if not attr.startswith('_')]
    print(f"Available attributes: {attrs}")
except Exception as e:
    print(f"Error listing attributes: {e}")

# Let's try inspecting the PDF model's source
print("\nTrying to locate the PDF class definition:")
import inspect
import os
import courses

module_file = inspect.getfile(courses.models)
print(f"Models module file: {module_file}")

with open(module_file, 'r') as f:
    content = f.read()
    
# Extract the PDFDocument class definition
import re
pdf_class = re.search(r'class PDFDocument\([^)]+\):(.*?)(?=class\s+\w+\(|\Z)', content, re.DOTALL)
if pdf_class:
    print("PDFDocument class definition found:")
    print(pdf_class.group(0)[:200] + "...") # Print first 200 chars
else:
    print("PDFDocument class definition not found in the source file.")

print("\nTrying to reload the module:")
from importlib import reload
try:
    reload(courses.models)
    print("Module reloaded!")
    
    # Check again after reload
    if hasattr(courses.models, 'PDFDocument'):
        print("PDFDocument found after reload!")
    else:
        print("PDFDocument still not found after reload.")
        
except Exception as e:
    print(f"Error reloading module: {e}")
