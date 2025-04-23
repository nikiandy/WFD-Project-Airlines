from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from flights.models import Flight, Airport
from passengers.models import Passenger

# SecurityCheck model - stores data for securitycheck entities
class SecurityCheck(models.Model):

    CHECK_TYPES = (
        ('standard', 'Standard Security Check'),
        ('enhanced', 'Enhanced Security Check'),
        ('random', 'Random Selection Check'),
        ('targeted', 'Targeted Security Check'),
        ('precheck', 'Pre-Check/Expedited'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('passed', 'Passed'),
        ('flagged', 'Flagged for Additional Screening'),
        ('denied', 'Denied Boarding'),
        ('completed', 'Completed'),
    )

    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='security_checks')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='security_checks')
    check_type = models.CharField(max_length=20, choices=CHECK_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    location = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='security_checks')
    checkpoint_id = models.CharField(max_length=20, blank=True)
    scheduled_time = models.DateTimeField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    conducted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='conducted_security_checks',
        blank=True
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supervised_security_checks',
        blank=True
    )

    screening_methods = models.CharField(
        max_length=255, 
        help_text="Comma-separated list of screening methods used"
    )
    notes = models.TextField(blank=True)
    items_found = models.TextField(blank=True, help_text="Description of any prohibited items found")
    action_taken = models.TextField(blank=True)

    risk_score = models.PositiveSmallIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Risk score from 0-100"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_security_checks'
    )

    # String representation of the model
    def __str__(self):
        return f"{self.get_check_type_display()} for {self.passenger} on {self.flight}"

    def start_check(self, conducted_by):

        from django.utils import timezone

        self.status = 'in_progress'
        self.start_time = timezone.now()
        self.conducted_by = conducted_by
        self.save(update_fields=['status', 'start_time', 'conducted_by'])

    def complete_check(self, status, notes=None, items_found=None, action_taken=None):

        from django.utils import timezone

        self.status = status
        self.end_time = timezone.now()

        if notes:
            self.notes = notes

        if items_found:
            self.items_found = items_found

        if action_taken:
            self.action_taken = action_taken

        self.save(update_fields=['status', 'end_time', 'notes', 'items_found', 'action_taken'])

    def calculate_duration(self):

        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60  
        return None

    class Meta:
        verbose_name = "Security Check"
        verbose_name_plural = "Security Checks"
        ordering = ['-scheduled_time']

# WatchList model - stores data for watchlist entities
class WatchList(models.Model):

    LIST_TYPES = (
        ('no_fly', 'No Fly List'),
        ('selectee', 'Selectee List'),
        ('enhanced_screening', 'Enhanced Screening List'),
        ('caution', 'Caution List'),
        ('vip', 'VIP List'),
    )

    name = models.CharField(max_length=100)
    list_type = models.CharField(max_length=20, choices=LIST_TYPES)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    managed_by = models.CharField(max_length=100, help_text="Organization managing this list")
    source = models.CharField(max_length=100, help_text="Source of the list data")

    restricted_access = models.BooleanField(default=True)
    authorized_roles = models.TextField(
        blank=True, 
        help_text="Comma-separated list of roles authorized to access this list"
    )

    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_watchlists'
    )

    # String representation of the model
    def __str__(self):
        return f"{self.name} ({self.get_list_type_display()})"

    class Meta:
        verbose_name = "Watch List"
        verbose_name_plural = "Watch Lists"
        ordering = ['list_type', 'name']

# WatchListEntry model - stores data for watchlistentry entities
class WatchListEntry(models.Model):

    RISK_LEVELS = (
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('severe', 'Severe Risk'),
    )

    watch_list = models.ForeignKey(WatchList, on_delete=models.CASCADE, related_name='entries')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationalities = models.CharField(max_length=255, help_text="Comma-separated list of nationalities")
    passport_numbers = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of passport numbers")

    passenger = models.ForeignKey(
        Passenger, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='watchlist_entries'
    )

    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS)
    reason = models.TextField()
    instructions = models.TextField(help_text="Action to be taken if matched")

    additional_identifiers = models.TextField(
        blank=True, 
        help_text="Additional identifying information, such as known aliases, addresses, etc."
    )
    biometric_data_available = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    added_by_agency = models.CharField(max_length=100)
    reference_number = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_risk_level_display()}"

    def is_valid(self):

        from django.utils import timezone
        today = timezone.now().date()

        if not self.is_active:
            return False

        if self.valid_until and today > self.valid_until:
            return False

        return today >= self.valid_from

    class Meta:
        verbose_name = "Watch List Entry"
        verbose_name_plural = "Watch List Entries"
        ordering = ['-risk_level', 'last_name', 'first_name']

# SecurityIncident model - stores data for securityincident entities
class SecurityIncident(models.Model):

    INCIDENT_TYPES = (
        ('prohibited_item', 'Prohibited Item'),
        ('suspicious_behavior', 'Suspicious Behavior'),
        ('security_breach', 'Security Breach'),
        ('threat', 'Threat'),
        ('documentation_issue', 'Documentation Issue'),
        ('disruptive_passenger', 'Disruptive Passenger'),
        ('impersonation', 'Impersonation'),
        ('other', 'Other'),
    )

    SEVERITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('investigating', 'Under Investigation'),
        ('contained', 'Contained'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')

    location = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='security_incidents')
    specific_location = models.CharField(max_length=100, help_text="Specific location within the airport")
    occurred_at = models.DateTimeField()
    reported_at = models.DateTimeField()

    flight = models.ForeignKey(
        Flight, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='security_incidents'
    )
    passengers_involved = models.ManyToManyField(
        Passenger, 
        blank=True,
        related_name='security_incidents'
    )
    staff_involved = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='involved_in_security_incidents'
    )

    initial_response = models.TextField()
    response_team_leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_security_responses'
    )
    authorities_notified = models.BooleanField(default=False)
    authorities_notified_at = models.DateTimeField(null=True, blank=True)
    external_agencies_involved = models.CharField(max_length=255, blank=True)

    action_taken = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    requires_followup = models.BooleanField(default=False)
    followup_notes = models.TextField(blank=True)
    followup_deadline = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_security_incidents'
    )

    # String representation of the model
    def __str__(self):
        return f"{self.get_incident_type_display()} at {self.location} - {self.get_severity_display()}"

    def escalate_severity(self, new_severity, reason):

        if self.severity != new_severity:
            self.severity = new_severity
            self.save(update_fields=['severity'])

            SecurityIncidentLog.objects.create(
                incident=self,
                action="severity_escalation",
                details=f"Severity escalated to {self.get_severity_display()}. Reason: {reason}"
            )

    def notify_authorities(self, agencies=None):

        from django.utils import timezone

        self.authorities_notified = True
        self.authorities_notified_at = timezone.now()

        if agencies:
            self.external_agencies_involved = agencies

        self.save(update_fields=['authorities_notified', 'authorities_notified_at', 'external_agencies_involved'])

    def resolve_incident(self, resolution_notes):

        from django.utils import timezone

        self.status = 'resolved'
        self.resolution_notes = resolution_notes
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolution_notes', 'resolved_at'])

    def close_incident(self):

        from django.utils import timezone

        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'closed_at'])

    class Meta:
        verbose_name = "Security Incident"
        verbose_name_plural = "Security Incidents"
        ordering = ['-occurred_at', '-severity']

# SecurityIncidentLog model - stores data for securityincidentlog entities
class SecurityIncidentLog(models.Model):

    ACTION_TYPES = (
        ('status_change', 'Status Change'),
        ('severity_escalation', 'Severity Escalation'),
        ('severity_deescalation', 'Severity De-escalation'),
        ('notification', 'Notification'),
        ('response', 'Response Action'),
        ('investigation', 'Investigation Update'),
        ('resolution', 'Resolution Update'),
        ('other', 'Other'),
    )

    incident = models.ForeignKey(SecurityIncident, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=25, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='security_incident_actions'
    )

    details = models.TextField()
    attachments = models.TextField(blank=True, help_text="Comma-separated list of attachment references")

    # String representation of the model
    def __str__(self):
        return f"{self.get_action_display()} on {self.incident} at {self.timestamp}"

    class Meta:
        verbose_name = "Security Incident Log"
        verbose_name_plural = "Security Incident Logs"
        ordering = ['-timestamp']

# SecuritySOP model - stores data for securitysop entities
class SecuritySOP(models.Model):

    CATEGORY_CHOICES = (
        ('passenger_screening', 'Passenger Screening'),
        ('baggage_screening', 'Baggage Screening'),
        ('access_control', 'Access Control'),
        ('incident_response', 'Incident Response'),
        ('threat_assessment', 'Threat Assessment'),
        ('documentation', 'Documentation Verification'),
        ('restricted_items', 'Restricted Items Handling'),
        ('special_cases', 'Special Cases'),
        ('general', 'General Procedures'),
    )

    title = models.CharField(max_length=200)
    document_id = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES)
    description = models.TextField()
    procedure_text = models.TextField()

    version = models.CharField(max_length=20)
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    supersedes = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='superseded_by'
    )

    is_classified = models.BooleanField(default=False)
    classification_level = models.CharField(max_length=50, blank=True)
    access_restricted_to = models.TextField(blank=True, help_text="Comma-separated list of roles with access")

    approved_by = models.CharField(max_length=100)
    approved_date = models.DateField()
    review_required_by = models.DateField()

    related_documents = models.TextField(blank=True, help_text="References to related documents")
    attachments = models.TextField(blank=True, help_text="Comma-separated list of attachment references")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_security_sops'
    )

    # String representation of the model
    def __str__(self):
        return f"{self.document_id}: {self.title} v{self.version}"

    def is_current(self):

        from django.utils import timezone
        today = timezone.now().date()

        if self.expiry_date and today > self.expiry_date:
            return False

        if SecuritySOP.objects.filter(supersedes=self).exists():
            return False

        return True

    class Meta:
        verbose_name = "Security SOP"
        verbose_name_plural = "Security SOPs"
        ordering = ['category', 'document_id'] 