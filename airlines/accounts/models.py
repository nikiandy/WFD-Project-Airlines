from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('planning_manager', 'Planning Manager'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # String representation of the model
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    def is_flight_manager(self):
        return self.is_superuser or self.role.lower() in ['admin', 'planning_manager']

# UserProfile model - stores data for userprofile entities
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)

    # String representation of the model
    def __str__(self):
        return f"Profile for {self.user.email}"
