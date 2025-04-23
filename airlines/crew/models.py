from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from flights.models import Flight, Aircraft, Airport, FlightSector

# CrewMember model - stores data for crewmember entities
class CrewMember(models.Model):

    CREW_TYPES = (
        ('pilot', 'Pilot'),
        ('first_officer', 'First Officer'),
        ('flight_engineer', 'Flight Engineer'),
        ('cabin_crew', 'Cabin Crew'),
        ('purser', 'Purser'),
        ('ground_crew', 'Ground Crew'),
    )

    EMPLOYMENT_STATUSES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contractor', 'Contractor'),
        ('trainee', 'Trainee'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='crew_profile'
    )
    crew_id = models.CharField(max_length=20, unique=True)
    crew_type = models.CharField(max_length=20, choices=CREW_TYPES)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUSES, default='full_time')

    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=50, unique=True)
    passport_expiry = models.DateField()
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    hire_date = models.DateField()
    base_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='based_crew')
    seniority_number = models.PositiveIntegerField(unique=True, null=True, blank=True)

    max_flight_hours_month = models.PositiveSmallIntegerField(default=100)
    max_flight_hours_year = models.PositiveSmallIntegerField(default=1000)
    rest_time_required = models.PositiveSmallIntegerField(default=12, help_text=_("Required rest time in hours"))

    notes = models.TextField(blank=True)
    profile_photo = models.CharField(max_length=255, blank=True, help_text=_("Path to profile photo"))
    profile_image = models.ImageField(upload_to='crew_photos/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.crew_id}) - {self.get_crew_type_display()}"

    def is_available(self, start_time, end_time):

        from django.db.models import Q
        from datetime import timedelta

        overlapping_schedules = self.schedules.filter(
            Q(start_time__lt=end_time, end_time__gt=start_time),
            Q(status__in=['assigned', 'confirmed', 'checked_in'])
        ).exists()

        if overlapping_schedules:
            return False

        overlapping_leave = self.leaves.filter(
            Q(start_date__lte=end_time.date(), end_date__gte=start_time.date()),
            Q(status='approved')
        ).exists()

        if overlapping_leave:
            return False

        previous_duty = self.schedules.filter(
            end_time__lt=start_time,
            status__in=['confirmed', 'completed', 'checked_in']
        ).order_by('-end_time').first()

        if previous_duty:
            min_rest_time = timedelta(hours=self.rest_time_required)
            if (start_time - previous_duty.end_time) < min_rest_time:
                return False

        return True

    def get_flight_hours(self, start_date, end_date):

        completed_schedules = self.schedules.filter(
            duty_type='flight',
            status__in=['completed', 'checked_in'],
            start_time__date__gte=start_date,
            end_time__date__lte=end_date
        )

        total_hours = 0
        for schedule in completed_schedules:
            duration = schedule.duration_hours()
            if duration:
                total_hours += duration

        return total_hours

    def get_active_qualifications(self):

        from django.utils import timezone
        today = timezone.now().date()

        return self.qualifications.filter(
            is_active=True
        ).filter(
            models.Q(expiry_date__isnull=True) | models.Q(expiry_date__gt=today)
        )

    def is_qualified_for_aircraft(self, aircraft):

        aircraft_type = aircraft.aircraft_type

        if self.crew_type in ['pilot', 'first_officer', 'flight_engineer']:
            return self.get_active_qualifications().filter(
                qualification_type='aircraft_type',
                aircraft_type=aircraft_type.model
            ).exists()

        return True

    class Meta:
        verbose_name = _("Crew Member")
        verbose_name_plural = _("Crew Members")
        ordering = ['crew_type', 'user__last_name', 'user__first_name']

# CrewQualification model - stores data for crewqualification entities
class CrewQualification(models.Model):

    QUALIFICATION_TYPES = (
        ('license', 'Flight License'),
        ('aircraft_type', 'Aircraft Type Rating'),
        ('medical', 'Medical Certification'),
        ('safety', 'Safety Training'),
        ('security', 'Security Training'),
        ('language', 'Language Proficiency'),
        ('instructor', 'Instructor Rating'),
        ('examiner', 'Examiner Rating'),
        ('special', 'Special Qualification'),
    )

    PROFICIENCY_LEVELS = (
        (1, 'Level 1 - Pre-Elementary'),
        (2, 'Level 2 - Elementary'),
        (3, 'Level 3 - Pre-Operational'),
        (4, 'Level 4 - Operational'),
        (5, 'Level 5 - Extended'),
        (6, 'Level 6 - Expert'),
    )

    crew_member = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='qualifications')
    qualification_type = models.CharField(max_length=20, choices=QUALIFICATION_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    certification_number = models.CharField(max_length=50, blank=True)
    issuing_authority = models.CharField(max_length=100)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)

    aircraft_type = models.CharField(max_length=50, blank=True, help_text=_("Aircraft type for type ratings"))
    proficiency_level = models.PositiveSmallIntegerField(
        choices=PROFICIENCY_LEVELS,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    restrictions = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    validation_method = models.CharField(max_length=100, blank=True, help_text=_("Method used to validate this qualification"))

    last_recurrent_training = models.DateField(null=True, blank=True)
    next_recurrent_training = models.DateField(null=True, blank=True)

    document_references = models.TextField(blank=True, help_text=_("Reference numbers for supporting documents"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_crew_qualifications'
    )

    # String representation of the model
    def __str__(self):
        return f"{self.crew_member.crew_id} - {self.title} ({self.get_qualification_type_display()})"

    def is_valid(self):

        from django.utils import timezone
        today = timezone.now().date()

        if not self.is_active:
            return False

        if self.expiry_date and self.expiry_date < today:
            return False

        if self.next_recurrent_training and self.next_recurrent_training < today:
            return False

        return True

    def days_until_expiry(self):

        if not self.expiry_date:
            return None

        from django.utils import timezone
        from datetime import datetime

        today = timezone.now().date()
        if self.expiry_date < today:
            return -1 * (today - self.expiry_date).days  

        return (self.expiry_date - today).days

    class Meta:
        verbose_name = _("Crew Qualification")
        verbose_name_plural = _("Crew Qualifications")
        ordering = ['crew_member', 'qualification_type', '-issue_date']
        unique_together = [['crew_member', 'qualification_type', 'title', 'issue_date']]

# CrewSchedule model - stores data for crewschedule entities
class CrewSchedule(models.Model):

    DUTY_TYPES = (
        ('flight', 'Flight Duty'),
        ('standby', 'Standby Duty'),
        ('reserve', 'Reserve Duty'),
        ('training', 'Training'),
        ('ground', 'Ground Duty'),
        ('office', 'Office Duty'),
        ('simulator', 'Simulator Session'),
    )

    STATUS_CHOICES = (
        ('tentative', 'Tentative'),
        ('assigned', 'Assigned'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('reassigned', 'Reassigned'),
    )

    ROLE_CHOICES = (
        ('captain', 'Captain'),
        ('first_officer', 'First Officer'),
        ('flight_engineer', 'Flight Engineer'),
        ('cabin_manager', 'Cabin Manager/Purser'),
        ('cabin_crew', 'Cabin Crew'),
        ('instructor', 'Instructor'),
        ('trainee', 'Trainee'),
        ('observer', 'Observer'),
    )

    crew_member = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='schedules')
    duty_type = models.CharField(max_length=20, choices=DUTY_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='tentative')

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    report_time = models.DateTimeField(null=True, blank=True)
    debrief_time = models.DateTimeField(null=True, blank=True)

    flight = models.ForeignKey(
        Flight, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='crew_schedules'
    )
    flight_sector = models.ForeignKey(
        FlightSector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crew_schedules'
    )
    aircraft = models.ForeignKey(
        Aircraft,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crew_schedules'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)

    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crew_departures'
    )
    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crew_arrivals'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_crew_schedules'
    )

    # String representation of the model
    def __str__(self):
        schedule_type = f"{self.get_duty_type_display()}"
        if self.flight:
            return f"{self.crew_member.crew_id} - {schedule_type} - {self.flight.flight_number} ({self.start_time.date()})"
        return f"{self.crew_member.crew_id} - {schedule_type} - {self.start_time.date()}"

    def duration_hours(self):

        if self.end_time and self.start_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 3600
        return None

    def check_in(self):

        from django.utils import timezone

        self.status = 'checked_in'
        self.check_in_time = timezone.now()
        self.save(update_fields=['status', 'check_in_time'])

    def check_out(self):

        from django.utils import timezone

        self.status = 'completed'
        self.check_out_time = timezone.now()
        self.save(update_fields=['status', 'check_out_time'])

    def cancel(self, reason=None):

        self.status = 'canceled'
        if reason:
            self.notes += f"\nCanceled: {reason}"
        self.save(update_fields=['status', 'notes'])

    class Meta:
        verbose_name = _("Crew Schedule")
        verbose_name_plural = _("Crew Schedules")
        ordering = ['-start_time']

# CrewLeave model - stores data for crewleave entities
class CrewLeave(models.Model):

    LEAVE_TYPES = (
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('compassionate', 'Compassionate Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('training', 'Training Leave'),
        ('special', 'Special Leave'),
        ('compensatory', 'Compensatory Off'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    )

    crew_member = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.TextField()
    medical_certificate = models.CharField(max_length=255, blank=True, help_text=_("Reference to medical certificate if applicable"))

    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_crew_leaves'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation of the model
    def __str__(self):
        return f"{self.crew_member.crew_id} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"

    def duration_days(self):

        if self.end_date and self.start_date:
            delta = self.end_date - self.start_date
            return delta.days + 1  
        return None

    def approve(self, approver, notes=None):

        from django.utils import timezone

        self.status = 'approved'
        self.approved_by = approver
        self.approved_at = timezone.now()

        if notes:
            self.approval_notes = notes

        self.save(update_fields=[
            'status', 'approved_by', 'approved_at', 'approval_notes'
        ])

    def deny(self, approver, reason):

        from django.utils import timezone

        self.status = 'denied'
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.approval_notes = reason

        self.save(update_fields=[
            'status', 'approved_by', 'approved_at', 'approval_notes'
        ])

    def cancel(self):

        self.status = 'canceled'
        self.save(update_fields=['status'])

    class Meta:
        verbose_name = _("Crew Leave")
        verbose_name_plural = _("Crew Leaves")
        ordering = ['-start_date']

# CrewPayroll model - stores data for crewpayroll entities
class CrewPayroll(models.Model):

    crew_member = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='payroll_records')
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    payment_date = models.DateField()

    scheduled_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    standby_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    ground_duty_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    base_pay = models.DecimalField(max_digits=10, decimal_places=2)
    flight_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_diem = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_finalized = models.BooleanField(default=False)
    finalized_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_crew_payrolls'
    )

    # String representation of the model
    def __str__(self):
        return f"{self.crew_member.crew_id} - Payroll {self.pay_period_start} to {self.pay_period_end}"

    def calculate_total_pay(self):

        total = (
            self.base_pay +
            self.flight_pay +
            self.overtime_pay +
            self.allowances +
            self.per_diem -
            self.deductions
        )
        return total

    def finalize(self, reference=None):

        from django.utils import timezone

        if self.is_finalized:
            return

        self.is_finalized = True
        self.finalized_at = timezone.now()

        if reference:
            self.payment_reference = reference

        self.save(update_fields=[
            'is_finalized', 'finalized_at', 'payment_reference'
        ])

    class Meta:
        verbose_name = _("Crew Payroll")
        verbose_name_plural = _("Crew Payrolls")
        ordering = ['-pay_period_end', 'crew_member']
        unique_together = [['crew_member', 'pay_period_start', 'pay_period_end']] 