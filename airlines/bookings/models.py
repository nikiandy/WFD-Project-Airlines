from django.db import models
from django.conf import settings
from flights.models import FlightSchedule, Flight
import random
import string

# Passenger model - stores data for passenger entities
class Passenger(models.Model):

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=(
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ))

    email = models.EmailField()
    phone = models.CharField(max_length=20)

    passport_number = models.CharField(max_length=20, blank=True)
    passport_expiry = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100)

    special_requirements = models.TextField(blank=True)
    special_assistance = models.BooleanField(default=False)
    dietary_requirements = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def is_adult(self):
        from datetime import date, timedelta
        return (date.today() - self.date_of_birth).days >= 18 * 365

    class Meta:
        verbose_name = "Passenger"
        verbose_name_plural = "Passengers"

# Booking model - stores data for booking entities
class Booking(models.Model):

    reference_number = models.CharField(max_length=10, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)

    PAYMENT_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    )
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    additional_services_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    extra_baggage = models.IntegerField(default=0)
    has_oversized_baggage = models.BooleanField(default=False)
    has_sport_equipment = models.BooleanField(default=False)

    meal_preference = models.CharField(max_length=20, choices=(
        ('standard', 'Standard'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('gluten_free', 'Gluten Free'),
        ('kosher', 'Kosher'),
        ('halal', 'Halal'),
        ('diabetic', 'Diabetic'),
        ('low_sodium', 'Low Sodium'),
    ), default='standard')
    has_premium_meal = models.BooleanField(default=False)

    has_priority_boarding = models.BooleanField(default=False)
    has_travel_insurance = models.BooleanField(default=False)
    has_airport_pickup = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.reference_number} - {self.status}"

    def cancel_booking(self):

        self.status = 'cancelled'
        self.save()

    def is_paid(self):
        return self.payment_status == 'paid'

    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]

    def passenger_count(self):
        from passengers.models import PassengerBooking
        return PassengerBooking.objects.filter(booking=self).count()

    def get_first_passenger_booking(self):
        from passengers.models import PassengerBooking
        return PassengerBooking.objects.filter(booking=self).first()

    def get_total_baggage_fees(self):
        from passengers.models import PassengerBooking
        return sum(pb.baggage_fee for pb in PassengerBooking.objects.filter(booking=self))

    def get_total_seat_fees(self):
        from passengers.models import PassengerBooking
        return sum(pb.seat_selection_fee for pb in PassengerBooking.objects.filter(booking=self))

    def get_additional_services_fees(self):
        return self.additional_services_amount

    def recalculate_total_amount(self):

        additional_amount = 0

        if self.extra_baggage:
            additional_amount += 35 * self.extra_baggage
        if self.has_oversized_baggage:
            additional_amount += 50
        if self.has_sport_equipment:
            additional_amount += 65
        if self.has_premium_meal:
            additional_amount += 15
        if self.has_priority_boarding:
            additional_amount += 10
        if self.has_travel_insurance:
            additional_amount += 25
        if self.has_airport_pickup:
            additional_amount += 45

        self.additional_services_amount = additional_amount
        self.total_amount = self.base_amount + self.tax_amount + additional_amount - self.discount_amount

    @staticmethod
    def generate_reference_number():

        while True:

            reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Booking.objects.filter(reference_number=reference).exists():
                return reference

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['-created_at']

# Payment model - stores data for payment entities
class Payment(models.Model):

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')

    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True)

    payment_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"Payment for {self.booking.reference_number} - {self.status}"

    def process_refund(self):

        self.status = 'refunded'
        self.save()

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
