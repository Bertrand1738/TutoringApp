"""Migration to move enrollment data from courses to enrollments app"""
from django.db import migrations


def move_enrollments_forward(apps, schema_editor):
    """Move enrollments from courses app to enrollments app"""
    try:
        OldEnrollment = apps.get_model('courses', 'Enrollment')
        NewEnrollment = apps.get_model('enrollments', 'Enrollment')
        db_alias = schema_editor.connection.alias
        
        # Move the data
        if 'courses_enrollment' in schema_editor.connection.introspection.table_names():
            old_enrollments = OldEnrollment.objects.using(db_alias).all()
            
            # Create new enrollments from old data
            new_enrollments = [
                NewEnrollment(
                    student=enrollment.student,
                    course=enrollment.course,
                    enrolled_at=enrollment.enrollment_date,
                    is_active=True
                )
                for enrollment in old_enrollments
            ]
            
            # Bulk create new enrollments if there are any
            if new_enrollments:
                NewEnrollment.objects.using(db_alias).bulk_create(new_enrollments)
    except Exception as e:
        print(f"Error moving enrollments forward: {e}")


def move_enrollments_backward(apps, schema_editor):
    """Move enrollments back to courses app"""
    try:
        OldEnrollment = apps.get_model('courses', 'Enrollment')
        NewEnrollment = apps.get_model('enrollments', 'Enrollment')
        db_alias = schema_editor.connection.alias
        
        # Move the data back
        new_enrollments = NewEnrollment.objects.using(db_alias).all()
        
        # Create old enrollments from new data
        old_enrollments = [
            OldEnrollment(
                student=enrollment.student,
                course=enrollment.course,
                enrollment_date=enrollment.enrolled_at
            )
            for enrollment in new_enrollments
        ]
        
        # Bulk create old enrollments if there are any
        if old_enrollments:
            OldEnrollment.objects.using(db_alias).bulk_create(old_enrollments)
    except Exception as e:
        print(f"Error moving enrollments backward: {e}")


class Migration(migrations.Migration):
    """Migration class for moving enrollment data"""
    dependencies = [
        ('enrollments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            code=move_enrollments_forward,
            reverse_code=move_enrollments_backward,
            hints={'target_db': 'default'},
            atomic=True
        ),
    ]
