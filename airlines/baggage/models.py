from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from flights.models import Flight, TravelClass
from bookings.models import Booking

# BaggagePolicy model - stores data for baggagepolicy entities
class BaggagePolicy(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField()

    cabin_baggage_allowed = models.BooleanField(default=True)
    cabin_baggage_max_count = models.PositiveSmallIntegerField(default=1)
    cabin_baggage_max_weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    cabin_baggage_max_dimensions = models.CharField(max_length=50, help_text="Format: LxWxH in cm")

    checked_baggage_allowed = models.BooleanField(default=True)
    checked_baggage_max_count = models.PositiveSmallIntegerField(default=1)
    checked_baggage_max_weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    checked_baggage_max_dimensions = models.CharField(max_length=50, help_text="Format: LxWxH in cm")

    sports_equipment_allowed = models.BooleanField(default=False)
    sports_equipment_fee = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )

    musical_instruments_allowed = models.BooleanField(default=False)
    musical_instruments_fee = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )

    excess_weight_fee_per_kg = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    additional_bag_fee = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )

    prohibited_items = models.TextField(help_text="Comma-separated list of prohibited items")

    applicable_flights = models.ManyToManyField(Flight, blank=True, related_name='baggage_policies')
    applicable_flight_classes = models.ManyToManyField(TravelClass, blank=True, related_name='baggage_policies')

    is_active = models.BooleanField(default=True)
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Baggage Policy"
        verbose_name_plural = "Baggage Policies"

# BaggageAllowance model - stores data for baggageallowance entities
class BaggageAllowance(models.Model):

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='baggage_allowance')
    policy = models.ForeignKey(BaggagePolicy, on_delete=models.PROTECT, related_name='allowances')

    cabin_baggage_count = models.PositiveSmallIntegerField(null=True, blank=True)
    cabin_baggage_weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )

    checked_baggage_count = models.PositiveSmallIntegerField(null=True, blank=True)
    checked_baggage_weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )

    extra_baggage_fee_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    has_sports_equipment = models.BooleanField(default=False)
    sports_equipment_description = models.CharField(max_length=255, blank=True)
    sports_equipment_fee_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    has_musical_instrument = models.BooleanField(default=False)
    musical_instrument_description = models.CharField(max_length=255, blank=True)
    musical_instrument_fee_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_baggage_allowances'
    )

    # String representation of the model
    def __str__(self):
        return f"Baggage allowance for {self.booking}"

    def get_cabin_baggage_count(self):

        return self.cabin_baggage_count if self.cabin_baggage_count is not None else self.policy.cabin_baggage_max_count

    def get_cabin_baggage_weight(self):

        return self.cabin_baggage_weight if self.cabin_baggage_weight is not None else self.policy.cabin_baggage_max_weight

    def get_checked_baggage_count(self):

        return self.checked_baggage_count if self.checked_baggage_count is not None else self.policy.checked_baggage_max_count

    def get_checked_baggage_weight(self):

        return self.checked_baggage_weight if self.checked_baggage_weight is not None else self.policy.checked_baggage_max_weight

    def calculate_total_fees(self):

        return self.extra_baggage_fee_paid + self.sports_equipment_fee_paid + self.musical_instrument_fee_paid

    class Meta:
        verbose_name = "Baggage Allowance"
        verbose_name_plural = "Baggage Allowances"

# BaggageItem model - stores data for baggageitem entities
class BaggageItem(models.Model):

    BAGGAGE_TYPES = (
        ('cabin', 'Cabin Baggage'),
        ('checked', 'Checked Baggage'),
        ('sports', 'Sports Equipment'),
        ('musical', 'Musical Instrument'),
        ('other', 'Other Special Item'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending Check-in'),
        ('checked_in', 'Checked In'),
        ('in_transit', 'In Transit'),
        ('arrived', 'Arrived at Destination'),
        ('claimed', 'Claimed by Passenger'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    )

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='baggage_items')
    passenger = models.ForeignKey('passengers.Passenger', on_delete=models.CASCADE, related_name='baggage_items')
    baggage_type = models.CharField(max_length=20, choices=BAGGAGE_TYPES)
    description = models.CharField(max_length=255)

    weight = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    dimensions = models.CharField(max_length=50, help_text="Format: LxWxH in cm")
    color = models.CharField(max_length=50, blank=True)

    tag_number = models.CharField(max_length=20, unique=True)
    barcode = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='checked_in_baggage',
        blank=True
    )
    checked_in_location = models.CharField(max_length=100, blank=True)

    claimed_at = models.DateTimeField(null=True, blank=True)
    claiming_location = models.CharField(max_length=100, blank=True)

    requires_special_handling = models.BooleanField(default=False)
    special_handling_instructions = models.TextField(blank=True)
    contains_fragile_items = models.BooleanField(default=False)
    contains_dangerous_goods = models.BooleanField(default=False)

    is_insured = models.BooleanField(default=False)
    declared_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )

    has_issues = models.BooleanField(default=False)
    issue_description = models.TextField(blank=True)
    issue_reported_at = models.DateTimeField(null=True, blank=True)
    issue_resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.get_baggage_type_display()} - {self.tag_number}"

    def check_in(self, location, checked_in_by):

        from django.utils import timezone

        self.status = 'checked_in'
        self.checked_in_at = timezone.now()
        self.checked_in_by = checked_in_by
        self.checked_in_location = location
        self.save(update_fields=['status', 'checked_in_at', 'checked_in_by', 'checked_in_location'])

    def mark_claimed(self, location):

        from django.utils import timezone

        self.status = 'claimed'
        self.claimed_at = timezone.now()
        self.claiming_location = location
        self.save(update_fields=['status', 'claimed_at', 'claiming_location'])

    def report_issue(self, issue_description):

        from django.utils import timezone

        self.has_issues = True
        self.issue_description = issue_description
        self.issue_reported_at = timezone.now()

        if 'lost' in issue_description.lower():
            self.status = 'lost'
        elif 'damage' in issue_description.lower():
            self.status = 'damaged'

        self.save(update_fields=['has_issues', 'issue_description', 'issue_reported_at', 'status'])

    def resolve_issue(self):

        from django.utils import timezone

        self.issue_resolved_at = timezone.now()
        self.save(update_fields=['issue_resolved_at'])

    class Meta:
        verbose_name = "Baggage Item"
        verbose_name_plural = "Baggage Items"
        ordering = ['-created_at']

# BaggageTransfer model - stores data for baggagetransfer entities
class BaggageTransfer(models.Model):

    baggage_item = models.ForeignKey(BaggageItem, on_delete=models.CASCADE, related_name='transfers')
    origin_flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='baggage_transfers_from')
    destination_flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='baggage_transfers_to')

    transfer_date = models.DateTimeField()
    transfer_location = models.CharField(max_length=100)
    transfer_status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='scheduled'
    )

    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='handled_baggage_transfers'
    )
    notes = models.TextField(blank=True)

    scheduled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # String representation of the model
    def __str__(self):
        return f"Transfer of {self.baggage_item} from {self.origin_flight} to {self.destination_flight}"

    def complete_transfer(self, handler):

        from django.utils import timezone

        self.transfer_status = 'completed'
        self.handled_by = handler
        self.completed_at = timezone.now()
        self.save(update_fields=['transfer_status', 'handled_by', 'completed_at'])

    class Meta:
        verbose_name = "Baggage Transfer"
        verbose_name_plural = "Baggage Transfers"
        ordering = ['transfer_date'] 