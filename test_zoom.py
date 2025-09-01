"""
Manual test script for Zoom integration
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.services.zoom import ZoomMeetingService

def test_zoom_integration():
    """Test Zoom integration with real credentials"""
    zoom = ZoomMeetingService()
    
    # Test meeting creation
    print("\nTesting meeting creation...")
    try:
        meeting = zoom.create_meeting(
            topic="Test French Lesson",
            start_time=datetime.now() + timedelta(hours=1),
            duration_minutes=60,
            teacher_email="your_zoom_email@example.com"  # Replace with real email
        )
        print("✅ Meeting created successfully!")
        print(f"Meeting ID: {meeting['id']}")
        print(f"Join URL: {meeting['join_url']}")
        print(f"Password: {meeting['password']}")
        
        # Test getting meeting details
        print("\nTesting get meeting details...")
        meeting_details = zoom.get_meeting(meeting['id'])
        print("✅ Meeting details retrieved successfully!")
        
        # Test updating meeting
        print("\nTesting meeting update...")
        zoom.update_meeting(
            meeting['id'],
            topic="Updated French Lesson"
        )
        print("✅ Meeting updated successfully!")
        
        # Test meeting deletion
        print("\nTesting meeting deletion...")
        zoom.delete_meeting(meeting['id'])
        print("✅ Meeting deleted successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    test_zoom_integration()
