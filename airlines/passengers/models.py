from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

from flights.models import Flight, Airport, TravelClass  
from bookings.models import Booking, Passenger as BookingPassenger

# Passenger model - stores data for passenger entities
class Passenger(models.Model):

    TITLE_CHOICES = (
        ('mr', 'Mr'),
        ('mrs', 'Mrs'),
        ('ms', 'Ms'),
        ('miss', 'Miss'),
        ('dr', 'Dr'),
        ('prof', 'Prof'),
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='passenger_profile'
    )

    passenger_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=100)

    email = models.EmailField(blank=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )

    passport_number = models.CharField(max_length=50, blank=True)
    passport_issuing_country = models.CharField(max_length=100, blank=True)
    passport_expiry = models.DateField(null=True, blank=True)

    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    special_assistance = models.TextField(blank=True, help_text=_("Any special assistance requirements"))
    dietary_requirements = models.TextField(blank=True, help_text=_("Any special dietary requirements"))

    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.passenger_id})"

    def get_full_name(self):

        full_name = f"{self.first_name}"
        if self.middle_name:
            full_name += f" {self.middle_name}"
        full_name += f" {self.last_name}"

        if self.title:
            title_display = dict(self.TITLE_CHOICES).get(self.title, '')
            return f"{title_display} {full_name}"

        return full_name

    def is_adult(self):

        from django.utils import timezone
        from dateutil.relativedelta import relativedelta

        today = timezone.now().date()
        age = relativedelta(today, self.date_of_birth).years

        return age >= 18

    def get_age(self):

        from django.utils import timezone
        from dateutil.relativedelta import relativedelta

        today = timezone.now().date()
        age = relativedelta(today, self.date_of_birth).years

        return age

    def has_valid_passport(self):

        if not self.passport_number or not self.passport_expiry:
            return False

        from django.utils import timezone
        today = timezone.now().date()

        return self.passport_expiry > today

    def passport_validity_days(self):

        if not self.passport_expiry:
            return None

        from django.utils import timezone
        today = timezone.now().date()

        return (self.passport_expiry - today).days

    def blacklist(self, reason):

        self.is_blacklisted = True
        self.blacklist_reason = reason
        self.save(update_fields=['is_blacklisted', 'blacklist_reason'])

    def remove_from_blacklist(self):

        self.is_blacklisted = False
        self.save(update_fields=['is_blacklisted'])

    class Meta:
        verbose_name = _("Passenger")
        verbose_name_plural = _("Passengers")
        ordering = ['last_name', 'first_name']

# PassengerBooking model - stores data for passengerbooking entities
class PassengerBooking(models.Model):

    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='passenger_bookings')
    passenger = models.ForeignKey(BookingPassenger, on_delete=models.CASCADE, related_name='passenger_bookings')
    flight = models.ForeignKey('flights.Flight', on_delete=models.CASCADE, related_name='passenger_bookings')

    flight_class = models.ForeignKey(TravelClass, on_delete=models.SET_NULL, null=True, related_name='passenger_bookings')

    PASSENGER_TYPE_CHOICES = (
        ('adult', 'Adult'),
        ('child', 'Child'),
        ('infant', 'Infant'),
    )
    passenger_type = models.CharField(max_length=10, choices=PASSENGER_TYPE_CHOICES)

    seat_number = models.CharField(max_length=5, blank=True)
    seat_selection_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    checked_baggage = models.BooleanField(default=False)
    carry_on_baggage = models.BooleanField(default=True)
    extra_baggage = models.BooleanField(default=False)
    baggage_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    STATUS_CHOICES = (
        ('booked', 'Booked'),
        ('checked_in', 'Checked In'),
        ('boarded', 'Boarded'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')

    checked_in = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)

    boarded = models.BooleanField(default=False)
    boarding_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.passenger} - {self.flight}"

    def check_in(self):

        from django.utils import timezone
        self.checked_in = True
        self.check_in_time = timezone.now()
        self.status = 'checked_in'
        self.save()

    def board(self):

        from django.utils import timezone
        self.boarded = True
        self.boarding_time = timezone.now()
        self.status = 'boarded'
        self.save()

    def cancel(self):

        self.status = 'cancelled'
        self.save()

    def get_total_fee(self):

        return self.base_fare + self.baggage_fee + self.seat_selection_fee

    class Meta:
        verbose_name = "Passenger Booking"
        verbose_name_plural = "Passenger Bookings"
        unique_together = ('booking', 'passenger', 'flight')

# LoyaltyProgram model - stores data for loyaltyprogram entities
class LoyaltyProgram(models.Model):

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    terms_and_conditions = models.TextField()

    points_expiry_months = models.PositiveSmallIntegerField(default=36)
    min_points_redemption = models.PositiveIntegerField(default=1000)
    points_currency_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0.01,
        help_text=_("Value of 1 point in currency")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = _("Loyalty Program")
        verbose_name_plural = _("Loyalty Programs")

# LoyaltyTier model - stores data for loyaltytier entities
class LoyaltyTier(models.Model):

    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='tiers')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    description = models.TextField()

    min_points_earned = models.PositiveIntegerField(help_text=_("Minimum points to qualify for this tier"))
    min_flights_count = models.PositiveSmallIntegerField(default=0)

    points_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    baggage_allowance_bonus = models.PositiveSmallIntegerField(default=0, help_text=_("Additional baggage in kg"))
    priority_check_in = models.BooleanField(default=False)
    priority_boarding = models.BooleanField(default=False)
    lounge_access = models.BooleanField(default=False)
    companion_tickets = models.PositiveSmallIntegerField(default=0)
    seat_upgrade_vouchers = models.PositiveSmallIntegerField(default=0)

    additional_benefits = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.program.code} - {self.name}"

    class Meta:
        verbose_name = _("Loyalty Tier")
        verbose_name_plural = _("Loyalty Tiers")
        ordering = ['program', 'min_points_earned']
        unique_together = [['program', 'code']]

# LoyaltyMembership model - stores data for loyaltymembership entities
class LoyaltyMembership(models.Model):

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    )

    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='memberships')
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='loyalty_memberships')
    membership_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    current_tier = models.ForeignKey(
        LoyaltyTier,
        on_delete=models.SET_NULL,
        null=True,
        related_name='members'
    )
    tier_qualification_date = models.DateField(null=True, blank=True)
    tier_expiry_date = models.DateField(null=True, blank=True)

    current_points = models.PositiveIntegerField(default=0)
    lifetime_points = models.PositiveIntegerField(default=0)
    pending_points = models.PositiveIntegerField(default=0)

    join_date = models.DateField()
    last_activity_date = models.DateField(null=True, blank=True)
    last_flight_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.membership_number} - {self.passenger}"

    def add_points(self, points, description=None):

        self.current_points += points
        self.lifetime_points += points

        from django.utils import timezone
        self.last_activity_date = timezone.now().date()

        self.save(update_fields=['current_points', 'lifetime_points', 'last_activity_date'])

        LoyaltyTransaction.objects.create(
            membership=self,
            transaction_type='earn',
            points=points,
            description=description or 'Points credited'
        )

        self.check_tier_upgrade()

    def deduct_points(self, points, description=None):

        if self.current_points < points:
            return False

        self.current_points -= points

        from django.utils import timezone
        self.last_activity_date = timezone.now().date()

        self.save(update_fields=['current_points', 'last_activity_date'])

        LoyaltyTransaction.objects.create(
            membership=self,
            transaction_type='redeem',
            points=points,
            description=description or 'Points redeemed'
        )

        return True

    def check_tier_upgrade(self):

        eligible_tiers = self.program.tiers.filter(
            min_points_earned__lte=self.lifetime_points
        ).order_by('-min_points_earned')

        if eligible_tiers.exists():
            highest_eligible_tier = eligible_tiers.first()

            if not self.current_tier or self.current_tier.id != highest_eligible_tier.id:
                self.current_tier = highest_eligible_tier

                from django.utils import timezone
                today = timezone.now().date()

                self.tier_qualification_date = today
                from dateutil.relativedelta import relativedelta
                self.tier_expiry_date = today + relativedelta(years=1)

                self.save(update_fields=['current_tier', 'tier_qualification_date', 'tier_expiry_date'])

                return True

        return False

    def expire_points(self, age_months=None):

        if not age_months:
            age_months = self.program.points_expiry_months

        from django.utils import timezone
        from dateutil.relativedelta import relativedelta

        expiry_date = timezone.now().date() - relativedelta(months=age_months)

        transactions_to_expire = self.transactions.filter(
            transaction_type='earn',
            is_expired=False,
            transaction_date__lt=expiry_date
        )

        total_expired = 0
        for transaction in transactions_to_expire:

            if transaction.remaining_points <= 0:
                continue

            points_to_expire = transaction.remaining_points
            total_expired += points_to_expire

            transaction.is_expired = True
            transaction.save(update_fields=['is_expired'])

            LoyaltyTransaction.objects.create(
                membership=self,
                transaction_type='expire',
                points=points_to_expire,
                description=f"Points expired from transaction {transaction.id}"
            )

        if total_expired > 0:
            self.current_points = max(0, self.current_points - total_expired)
            self.save(update_fields=['current_points'])

        return total_expired

    class Meta:
        verbose_name = _("Loyalty Membership")
        verbose_name_plural = _("Loyalty Memberships")
        unique_together = [['program', 'passenger']]

# LoyaltyTransaction model - stores data for loyaltytransaction entities
class LoyaltyTransaction(models.Model):

    TRANSACTION_TYPES = (
        ('earn', 'Earn Points'),
        ('redeem', 'Redeem Points'),
        ('expire', 'Points Expired'),
        ('adjust', 'Points Adjustment'),
        ('transfer', 'Points Transfer'),
        ('bonus', 'Bonus Points'),
    )

    membership = models.ForeignKey(LoyaltyMembership, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.PositiveIntegerField()
    remaining_points = models.PositiveIntegerField(null=True, blank=True)

    booking = models.ForeignKey(
        PassengerBooking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loyalty_transactions'
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loyalty_transactions'
    )

    transaction_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    is_expired = models.BooleanField(default=False)
    reference_code = models.CharField(max_length=50, blank=True)

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_loyalty_transactions'
    )

    # String representation of the model
    def __str__(self):
        return f"{self.membership.membership_number} - {self.get_transaction_type_display()} - {self.points} pts"

    # Override save method to add custom behavior
    def save(self, *args, **kwargs):

        if self.transaction_type == 'earn' and self.remaining_points is None:
            self.remaining_points = self.points

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Loyalty Transaction")
        verbose_name_plural = _("Loyalty Transactions")
        ordering = ['-transaction_date'] 