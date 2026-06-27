from django.db import models
from django.contrib.auth.models import User


class JobAnalysis(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    email = models.CharField(max_length=200)

    phone = models.CharField(max_length=50, blank=True, null=True)
    salary = models.CharField(max_length=100)

    fee = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    decision = models.CharField(max_length=50)
    confidence = models.FloatField()

    reasons = models.TextField(blank=True, null=True)
    justification = models.TextField(blank=True, null=True)

    analysis_type = models.CharField(max_length=20, default="text")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_title} - {self.decision}"

# ================= USER PROFILE (ROLE SYSTEM) =================

class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("USER", "User"),
        ("ADMIN", "Admin")
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="USER"
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"