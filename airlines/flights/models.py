from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import uuid
from datetime import timedelta
from django.urls import reverse
from accounts.models import User

# TravelClass model - stores data for travelclass entities
class TravelClass(models.Model):
    CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('premium_economy', 'Premium Economy'),
        ('business', 'Business'),
        ('first', 'First Class')
    ]

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price_factor = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)

    has_priority_boarding = models.BooleanField(default=False)
    has_lounge_access = models.BooleanField(default=False)
    baggage_allowance_kg = models.PositiveSmallIntegerField(default=20)
    has_extra_legroom = models.BooleanField(default=False)
    meal_service = models.CharField(
        max_length=20,
        choices=[
            ('standard', 'Standard Meal'),
            ('premium', 'Premium Meal'),
            ('luxury', 'Luxury Meal'),
            ('none', 'No Meal Service')
        ],
        default='standard'
    )
    display_order = models.PositiveSmallIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    # String representation of the model
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Travel Class"
        verbose_name_plural = "Travel Classes"
        ordering = ['display_order', 'price_factor']

# Airport model - stores data for airport entities
class Airport(models.Model):
    code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    timezone = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    terminal_count = models.PositiveSmallIntegerField(default=1)
    gate_count = models.PositiveSmallIntegerField(default=10)

    # String representation of the model
    def __str__(self):
        return f"{self.city} ({self.code}) - {self.name}"

    class Meta:
        ordering = ['code']

    # Get URL for this object
    def get_absolute_url(self):
        return reverse('airport_detail', kwargs={'code': self.code})

# AircraftType model - stores data for aircrafttype entities
class AircraftType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    cargo_capacity_kg = models.PositiveIntegerField(default=0)
    max_passengers = models.PositiveSmallIntegerField()
    max_range_km = models.PositiveIntegerField()
    cruise_speed_kmh = models.PositiveIntegerField()

    # String representation of the model
    def __str__(self):
        return f"{self.manufacturer} {self.model} ({self.code})"

    class Meta:
        verbose_name = "Aircraft Type"
        verbose_name_plural = "Aircraft Types"
        ordering = ['manufacturer', 'model']

# Aircraft model - stores data for aircraft entities
class Aircraft(models.Model):
    MODEL_CHOICES = [
        ('737-800', 'Boeing 737-800'),
        ('737-900', 'Boeing 737-900'),
        ('A320', 'Airbus A320'),
        ('A321', 'Airbus A321'),
        ('A330', 'Airbus A330'),
        ('787-9', 'Boeing 787-9 Dreamliner'),
        ('A350', 'Airbus A350'),
    ]

    registration = models.CharField(max_length=10, primary_key=True)
    model = models.CharField(max_length=20, choices=MODEL_CHOICES)
    capacity_economy = models.PositiveIntegerField(default=180)
    capacity_premium = models.PositiveIntegerField(default=30)
    capacity_business = models.PositiveIntegerField(default=20)
    capacity_first = models.PositiveIntegerField(default=10)
    in_service_date = models.DateField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    # String representation of the model
    def __str__(self):
        return f"{self.registration} ({self.model})"

    class Meta:
        verbose_name = "Aircraft"
        verbose_name_plural = "Aircraft"

# Route model - stores data for route entities
class Route(models.Model):
    origin = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='departures')
    destination = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='arrivals')
    distance_km = models.PositiveIntegerField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # String representation of the model
    def __str__(self):
        return f"{self.origin.code} → {self.destination.code}"

    class Meta:
        unique_together = ['origin', 'destination']

    # Get URL for this object
    def get_absolute_url(self):
        return reverse('route_detail', kwargs={
            'origin': self.origin.code,
            'destination': self.destination.code
        })

    # Override save method to add custom behavior
    def save(self, *args, **kwargs):
        if not self.duration_minutes and self.distance_km:
            avg_speed_kmh = 850
            self.duration_minutes = int((self.distance_km / avg_speed_kmh) * 60)

        super().save(*args, **kwargs)

# FlightSchedule model - stores data for flightschedule entities
class FlightSchedule(models.Model):
    flight_number = models.CharField(max_length=10)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.PROTECT)

    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    operates_monday = models.BooleanField(default=False)
    operates_tuesday = models.BooleanField(default=False)
    operates_wednesday = models.BooleanField(default=False)
    operates_thursday = models.BooleanField(default=False)
    operates_friday = models.BooleanField(default=False)
    operates_saturday = models.BooleanField(default=False)
    operates_sunday = models.BooleanField(default=False)

    effective_from = models.DateField()
    effective_until = models.DateField(null=True, blank=True)

    economy_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    business_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    first_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)

    # String representation of the model
    def __str__(self):
        return f"{self.flight_number}: {self.route} {self.departure_time}"

    def get_days_display(self):
        days = []
        if self.operates_monday: days.append('Mon')
        if self.operates_tuesday: days.append('Tue')
        if self.operates_wednesday: days.append('Wed')
        if self.operates_thursday: days.append('Thu')
        if self.operates_friday: days.append('Fri')
        if self.operates_saturday: days.append('Sat')
        if self.operates_sunday: days.append('Sun')
        return ', '.join(days)
    get_days_display.short_description = 'Days'

    class Meta:
        verbose_name = "Flight Schedule"
        verbose_name_plural = "Flight Schedules"
        ordering = ['flight_number', 'departure_time']

# Flight model - stores data for flight entities
class Flight(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('delayed', 'Delayed'),
        ('boarding', 'Boarding'),
        ('in_air', 'In Air'),
        ('landed', 'Landed'),
        ('arrived', 'Arrived'),
        ('cancelled', 'Cancelled'),
    ]

    flight_number = models.CharField(max_length=10)
    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name='flights')
    aircraft = models.ForeignKey(Aircraft, on_delete=models.PROTECT, related_name='flights')
    scheduled_departure = models.DateTimeField()
    scheduled_arrival = models.DateTimeField()
    actual_departure = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    base_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(1)])
    available_travel_classes = models.ManyToManyField(TravelClass, blank=True, related_name='flights')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    # String representation of the model
    def __str__(self):
        departure_date = self.scheduled_departure.strftime('%Y-%m-%d')
        return f"{self.flight_number} ({departure_date}): {self.route}"

    class Meta:
        unique_together = ['flight_number', 'scheduled_departure']
        ordering = ['scheduled_departure']

    # Get URL for this object
    def get_absolute_url(self):
        return reverse('flight_detail', kwargs={
            'flight_number': self.flight_number,
            'departure_date': self.scheduled_departure.strftime('%Y-%m-%d')
        })

    # Override save method to add custom behavior
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

    @property
    def delay_minutes(self):
        if not self.actual_departure or not self.scheduled_departure:
            return 0

        delay = self.actual_departure - self.scheduled_departure
        return int(delay.total_seconds() / 60)

    @property
    def is_international(self):
        return self.route.origin.country != self.route.destination.country

    @property
    def is_delayed(self):
        return self.status == 'delayed' or (
            self.actual_departure and 
            self.actual_departure > self.scheduled_departure + timezone.timedelta(minutes=15)
        )

# Booking model - stores data for booking entities
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    booking_reference = models.CharField(max_length=8, unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='flight_bookings')
    flight = models.ForeignKey(Flight, on_delete=models.PROTECT, related_name='bookings')
    travel_class = models.CharField(max_length=20, choices=TravelClass.CLASS_CHOICES)
    passenger_count = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.booking_reference} - {self.user.email}"

    class Meta:
        ordering = ['-created_at']

    # Get URL for this object
    def get_absolute_url(self):
        return reverse('booking_detail', kwargs={'booking_reference': self.booking_reference})

# Passenger model - stores data for passenger entities
class Passenger(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='flight_passengers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    seat_number = models.CharField(max_length=4, blank=True, null=True)

    # String representation of the model
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        unique_together = ['booking', 'passport_number']

# FlightSector model - stores data for flightsector entities
class FlightSector(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='sectors')
    origin = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='sector_departures')
    destination = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='sector_arrivals')

    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    sequence = models.PositiveSmallIntegerField(default=1)
    distance_km = models.PositiveIntegerField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)

    # String representation of the model
    def __str__(self):
        return f"{self.flight.flight_number}: {self.origin.code} → {self.destination.code}"

    class Meta:
        verbose_name = "Flight Sector"
        verbose_name_plural = "Flight Sectors"
        ordering = ['flight', 'sequence']
        unique_together = ['flight', 'sequence']
