from django.db import models
from django.conf import settings
from flights.models import Flight, Route, FlightSchedule
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Promotion model - stores data for promotion entities
class Promotion(models.Model):

    PROMOTION_TYPES = (
        ('discount', 'Discount'),
        ('reward', 'Reward Points'),
        ('upgrade', 'Free Upgrade'),
        ('companion', 'Companion Offer'),
        ('lounge', 'Lounge Access'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()

    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reward_points = models.PositiveIntegerField(null=True, blank=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    minimum_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)

    is_first_time_only = models.BooleanField(default=False)
    is_member_only = models.BooleanField(default=False)
    required_membership_tier = models.CharField(max_length=50, null=True, blank=True)

    applicable_routes = models.ManyToManyField(Route, blank=True, related_name='promotions')
    applicable_flights = models.ManyToManyField(Flight, blank=True, related_name='promotions')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.name} ({self.code})"

    def is_valid(self):

        now = timezone.now()

        if not self.is_active:
            return False

        if now < self.start_date or now > self.end_date:
            return False

        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False

        return True

    def apply_promotion(self, booking_amount):

        if not self.is_valid():
            return booking_amount

        if self.promotion_type == 'discount':
            if self.discount_percentage:
                discount = booking_amount * (self.discount_percentage / 100)
                return booking_amount - discount
            elif self.discount_amount:
                return max(booking_amount - self.discount_amount, 0)

        return booking_amount

    def increment_usage(self):

        self.usage_count += 1
        self.save(update_fields=['usage_count'])

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"
        ordering = ['-start_date']

# Deal model - stores data for deal entities
class Deal(models.Model):

    DEAL_TYPES = (
        ('flash', 'Flash Sale'),
        ('seasonal', 'Seasonal Offer'),
        ('destination', 'Destination Special'),
        ('holiday', 'Holiday Package'),
        ('member', 'Member Exclusive'),
        ('last_minute', 'Last Minute Deal'),
    )

    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    deal_type = models.CharField(max_length=20, choices=DEAL_TYPES)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    image = models.CharField(max_length=255, blank=True, null=True, help_text=_("Path to image file"))

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    destination_names = models.TextField(blank=True, help_text=_("Comma-separated list of destination names"))
    applicable_flights = models.ManyToManyField(Flight, blank=True, related_name='deals')
    applicable_schedules = models.ManyToManyField(FlightSchedule, blank=True, related_name='deals')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return self.title

    def is_valid(self):

        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    class Meta:
        verbose_name = "Deal"
        verbose_name_plural = "Deals"
        ordering = ['-created_at']

# Notification model - stores data for notification entities
class Notification(models.Model):

    NOTIFICATION_TYPES = (
        ('promotion', 'Promotion Alert'),
        ('deal', 'Deal Alert'),
        ('price_drop', 'Price Drop Alert'),
        ('booking', 'Booking Update'),
        ('system', 'System Update'),
        ('news', 'News Update'),
    )

    DELIVERY_CHANNELS = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')

    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)

    delivery_channel = models.CharField(max_length=20, choices=DELIVERY_CHANNELS)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    related_promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    related_deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.notification_type} notification for {self.user.get_full_name()}: {self.title}"

    def mark_as_sent(self):

        self.is_sent = True
        self.sent_at = timezone.now()
        self.save(update_fields=['is_sent', 'sent_at'])

    def mark_as_read(self):

        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

# SubscriptionPreference model - stores data for subscriptionpreference entities
class SubscriptionPreference(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription_preferences')

    email_promotions = models.BooleanField(default=True)
    email_deals = models.BooleanField(default=True)
    email_price_alerts = models.BooleanField(default=True)
    email_newsletters = models.BooleanField(default=True)

    sms_promotions = models.BooleanField(default=False)
    sms_deals = models.BooleanField(default=False)
    sms_booking_updates = models.BooleanField(default=True)

    push_promotions = models.BooleanField(default=True)
    push_deals = models.BooleanField(default=True)
    push_price_alerts = models.BooleanField(default=True)
    push_booking_updates = models.BooleanField(default=True)

    email_frequency = models.CharField(
        max_length=10,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"Subscription preferences for {self.user.get_full_name()}"

    class Meta:
        verbose_name = "Subscription Preference"
        verbose_name_plural = "Subscription Preferences" 