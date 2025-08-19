from django.contrib.auth.models import User
from django.db import models

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    government_id = models.CharField(max_length=100, blank=True)
    subscription_type = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"StudentProfile<{self.user.username}>"

    @property
    def role(self):
        return 'student'


class TeacherProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    government_id = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    avg_rating = models.FloatField(default=0)

    def __str__(self):
        return f"TeacherProfile<{self.user.username}>"

    @property
    def role(self):
        return 'teacher'



