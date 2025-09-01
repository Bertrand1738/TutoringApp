"""
Simple script to test PDF model functionality
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import models
from courses.models import PDF, Course

def test_pdf_model():
    print('PDF model exists:', PDF is not None)
    
    try:
        course = Course.objects.first()
        if course:
            print(f'Found course: {course}')
            pdf = PDF(
                course=course, 
                title='Test PDF', 
                description='Testing PDF functionality'
            )
            print('PDF object created successfully')
            print(f'PDF object: {pdf}')
            
            # Save to database
            try:
                pdf.save()
                print('PDF saved to database!')
                
                # Retrieve from database
                saved_pdf = PDF.objects.get(title='Test PDF')
                print(f'Retrieved PDF from database: {saved_pdf}')
            except Exception as save_error:
                print('Error saving PDF:', save_error)
        else:
            print('No courses found in database')
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    test_pdf_model()
