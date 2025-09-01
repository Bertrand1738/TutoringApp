"""
A simple script to check the models for errors
"""
import os
import django
import traceback

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    # Import the models
    print("Importing models...")
    from courses.models import Video, PDF, Assignment, Quiz
    print("Models imported successfully!")
    
    print("Importing serializers...")
    from courses.content_serializers import VideoSerializer, PDFSerializer, AssignmentSerializer, QuizSerializer
    print("Serializers imported successfully!")

    # Test creating a simple instance
    print("Getting model fields...")
    video_fields = [field.name for field in Video._meta.fields]
    pdf_fields = [field.name for field in PDF._meta.fields]
    assignment_fields = [field.name for field in Assignment._meta.fields]
    quiz_fields = [field.name for field in Quiz._meta.fields]
    
    print("Video fields:", video_fields)
    print("PDF fields:", pdf_fields)
    print("Assignment fields:", assignment_fields)
    print("Quiz fields:", quiz_fields)

    # Write results to a file
    print("Writing results to file...")
    with open('model_check_output.txt', 'w') as f:
        f.write("Models imported successfully\n")
        f.write("\nVideo model fields: " + str(video_fields))
        f.write("\nPDF model fields: " + str(pdf_fields))
        f.write("\nAssignment model fields: " + str(assignment_fields))
        f.write("\nQuiz model fields: " + str(quiz_fields))
        f.write("\n\nAll models check completed successfully")
    
    print("Model check completed successfully!")
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    print(traceback.format_exc())
    
    # Try to write error to file
    try:
        with open('model_check_error.txt', 'w') as f:
            f.write(f"ERROR: {str(e)}\n\n")
            f.write(traceback.format_exc())
    except:
        pass
