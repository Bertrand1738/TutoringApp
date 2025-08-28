from django.db import migrations

def move_enrollments_forward(apps, schema_editor):
    OldEnrollment = apps.get_model('courses', 'Enrollment')
    NewEnrollment = apps.get_model('enrollments', 'Enrollment')
    
    for enrollment in OldEnrollment.objects.all():
        NewEnrollment.objects.create(
            student=enrollment.student,
            course=enrollment.course,
            enrolled_at=enrollment.enrollment_date,
            is_active=True
        )

def move_enrollments_backward(apps, schema_editor):
    OldEnrollment = apps.get_model('courses', 'Enrollment')
    NewEnrollment = apps.get_model('enrollments', 'Enrollment')
    
    for enrollment in NewEnrollment.objects.all():
        OldEnrollment.objects.create(
            student=enrollment.student,
            course=enrollment.course,
            enrollment_date=enrollment.enrolled_at
        )

class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0001_initial'),
        ('enrollments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            move_enrollments_forward,
            move_enrollments_backward
        )
    ]
