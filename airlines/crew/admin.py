from django.contrib import admin
from .models import CrewMember, CrewQualification, CrewSchedule, CrewLeave, CrewPayroll

class CrewQualificationInline(admin.TabularInline):
    model = CrewQualification
    extra = 1
    fields = ('qualification_type', 'title', 'issue_date', 'expiry_date', 'is_active')

@admin.register(CrewMember)

# Admin interface for CrewMember model
class CrewMemberAdmin(admin.ModelAdmin):
    list_display = ('crew_id', 'get_full_name', 'crew_type', 'base_airport', 'employment_status')
    list_filter = ('crew_type', 'employment_status', 'base_airport')
    search_fields = ('crew_id', 'user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'crew_id', 'crew_type', 'employment_status')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'nationality', 'passport_number', 'passport_expiry', 
                      'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Employment Information', {
            'fields': ('hire_date', 'base_airport', 'seniority_number')
        }),
        ('Work Restrictions', {
            'fields': ('max_flight_hours_month', 'max_flight_hours_year', 'rest_time_required')
        }),
        ('Additional Details', {
            'fields': ('notes', 'profile_photo')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    inlines = [CrewQualificationInline]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(CrewQualification)

# Admin interface for CrewQualification model
class CrewQualificationAdmin(admin.ModelAdmin):
    list_display = ('crew_member', 'qualification_type', 'title', 'issue_date', 'expiry_date', 'is_active', 'is_valid')
    list_filter = ('qualification_type', 'is_active', 'issuing_authority')
    search_fields = ('crew_member__crew_id', 'title', 'certification_number')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('crew_member', 'qualification_type', 'title', 'description')
        }),
        ('Details', {
            'fields': ('certification_number', 'issuing_authority', 'issue_date', 'expiry_date')
        }),
        ('Type Specific', {
            'fields': ('aircraft_type', 'proficiency_level', 'restrictions')
        }),
        ('Status', {
            'fields': ('is_active', 'validation_method')
        }),
        ('Training', {
            'fields': ('last_recurrent_training', 'next_recurrent_training')
        }),
        ('Documents', {
            'fields': ('document_references',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )

    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Valid'

@admin.register(CrewSchedule)

# Admin interface for CrewSchedule model
class CrewScheduleAdmin(admin.ModelAdmin):
    list_display = ('crew_member', 'duty_type', 'start_time', 'end_time', 'status', 'flight')
    list_filter = ('duty_type', 'status', 'start_time')
    search_fields = ('crew_member__crew_id', 'flight__flight_number', 'notes')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('crew_member', 'duty_type', 'status')
        }),
        ('Time Information', {
            'fields': ('start_time', 'end_time', 'report_time', 'debrief_time')
        }),
        ('Flight Details', {
            'fields': ('flight', 'flight_sector', 'aircraft', 'role')
        }),
        ('Status Tracking', {
            'fields': ('check_in_time', 'check_out_time')
        }),
        ('Location', {
            'fields': ('departure_airport', 'arrival_airport')
        }),
        ('Additional Details', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )

    actions = ['mark_as_checked_in', 'mark_as_completed', 'mark_as_canceled']

    def mark_as_checked_in(self, request, queryset):
        for schedule in queryset:
            if schedule.status in ['assigned', 'confirmed']:
                schedule.check_in()
        self.message_user(request, f"{queryset.count()} schedule(s) marked as checked in.")
    mark_as_checked_in.short_description = "Mark selected schedules as checked in"

    def mark_as_completed(self, request, queryset):
        for schedule in queryset:
            if schedule.status in ['checked_in', 'confirmed']:
                schedule.check_out()
        self.message_user(request, f"{queryset.count()} schedule(s) marked as completed.")
    mark_as_completed.short_description = "Mark selected schedules as completed"

    def mark_as_canceled(self, request, queryset):
        for schedule in queryset:
            if schedule.status not in ['completed', 'canceled']:
                schedule.cancel("Canceled by admin")
        self.message_user(request, f"{queryset.count()} schedule(s) marked as canceled.")
    mark_as_canceled.short_description = "Mark selected schedules as canceled"

@admin.register(CrewLeave)

# Admin interface for CrewLeave model
class CrewLeaveAdmin(admin.ModelAdmin):
    list_display = ('crew_member', 'leave_type', 'start_date', 'end_date', 'status', 'duration_days')
    list_filter = ('leave_type', 'status', 'start_date')
    search_fields = ('crew_member__crew_id', 'reason')
    readonly_fields = ('requested_at', 'created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('crew_member', 'leave_type', 'status')
        }),
        ('Time Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Details', {
            'fields': ('reason', 'medical_certificate')
        }),
        ('Approval', {
            'fields': ('requested_at', 'approved_by', 'approved_at', 'approval_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    actions = ['approve_leaves', 'deny_leaves', 'cancel_leaves']

    def approve_leaves(self, request, queryset):
        for leave in queryset.filter(status='pending'):
            leave.approve(request.user, "Approved by admin")
        self.message_user(request, f"{queryset.filter(status='pending').count()} leave(s) approved.")
    approve_leaves.short_description = "Approve selected leave requests"

    def deny_leaves(self, request, queryset):
        for leave in queryset.filter(status='pending'):
            leave.deny(request.user, "Denied by admin")
        self.message_user(request, f"{queryset.filter(status='pending').count()} leave(s) denied.")
    deny_leaves.short_description = "Deny selected leave requests"

    def cancel_leaves(self, request, queryset):
        for leave in queryset.exclude(status__in=['completed', 'canceled']):
            leave.cancel()
        self.message_user(request, f"{queryset.exclude(status__in=['completed', 'canceled']).count()} leave(s) canceled.")
    cancel_leaves.short_description = "Cancel selected leave requests"

@admin.register(CrewPayroll)

# Admin interface for CrewPayroll model
class CrewPayrollAdmin(admin.ModelAdmin):
    list_display = ('crew_member', 'pay_period_start', 'pay_period_end', 'calculate_total_pay', 'is_finalized')
    list_filter = ('is_finalized', 'pay_period_start')
    search_fields = ('crew_member__crew_id', 'payment_reference')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('crew_member', 'pay_period_start', 'pay_period_end', 'payment_date')
        }),
        ('Flight Hours and Duty', {
            'fields': ('scheduled_hours', 'actual_hours', 'overtime_hours', 'standby_hours', 'ground_duty_hours')
        }),
        ('Compensation', {
            'fields': ('base_pay', 'flight_pay', 'overtime_pay', 'allowances', 'per_diem', 'deductions')
        }),
        ('Status', {
            'fields': ('is_finalized', 'finalized_at', 'payment_reference')
        }),
        ('Additional Details', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )

    actions = ['finalize_payrolls']

    def finalize_payrolls(self, request, queryset):
        for payroll in queryset.filter(is_finalized=False):
            payroll.finalize(f"Finalized by {request.user.username} on admin")
        self.message_user(request, f"{queryset.filter(is_finalized=False).count()} payroll(s) finalized.")
    finalize_payrolls.short_description = "Finalize selected payrolls" 