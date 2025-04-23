from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class User(AbstractUser):

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    passport_number = models.CharField(max_length=20, blank=True)
    passport_expiry_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    notification_email = models.BooleanField(default=True)
    notification_sms = models.BooleanField(default=False)
    preferred_language = models.CharField(max_length=10, default='en')

    MEMBERSHIP_LEVELS = (
        ('none', 'None'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    )
    frequent_flyer_number = models.CharField(max_length=20, blank=True)
    membership_level = models.CharField(max_length=10, choices=MEMBERSHIP_LEVELS, default='none')
    loyalty_points = models.PositiveIntegerField(default=0)

    accepted_terms = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    # String representation of the model
    def __str__(self):
        return self.email if self.email else self.username

    def get_full_name(self):

        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):

        return self.first_name

    def add_loyalty_points(self, points):

        self.loyalty_points += points
        self.update_membership_level()
        self.save()

    def update_membership_level(self):

        if self.loyalty_points >= 100000:
            self.membership_level = 'platinum'
        elif self.loyalty_points >= 50000:
            self.membership_level = 'gold'
        elif self.loyalty_points >= 10000:
            self.membership_level = 'silver'
        else:
            self.membership_level = 'none' 