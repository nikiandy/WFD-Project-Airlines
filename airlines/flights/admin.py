from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    TravelClass, Airport, AircraftType, Aircraft, 
    Route, FlightSchedule, Flight
)

@admin.register(TravelClass)

# Admin interface for TravelClass model
class TravelClassAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'price_factor', 'baggage_allowance_kg', 'has_priority_boarding', 'display_order', 'is_active')
    list_filter = ('is_active', 'has_priority_boarding', 'has_lounge_access')
    search_fields = ('name', 'code')
    ordering = ('display_order', 'price_factor')

    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'price_factor', 'display_order', 'is_active')
        }),
        ('Baggage', {
            'fields': ('baggage_allowance_kg', 'cabin_baggage_allowance')
        }),
        ('Seating', {
            'fields': ('seat_pitch', 'seat_width', 'has_power_outlets')
        }),
        ('Services', {
            'fields': ('has_priority_boarding', 'has_priority_checkin', 'has_lounge_access', 
                      'has_wifi', 'has_entertainment', 'meal_service')
        }),
    )

@admin.register(Airport)

# Admin interface for Airport model
class AirportAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'country', 'is_active')
    list_filter = ('country', 'is_active')
    search_fields = ('code', 'name', 'city', 'country')
    ordering = ('code',)

    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'city', 'country', 'is_active', 'opened_date')
        }),
        ('Geographic Information', {
            'fields': ('latitude', 'longitude', 'timezone')
        }),
    )

@admin.register(AircraftType)

# Admin interface for AircraftType model
class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'manufacturer', 'model', 'max_passengers', 'max_range_km')
    list_filter = ('manufacturer',)
    search_fields = ('code', 'name', 'manufacturer', 'model')

    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'manufacturer', 'model')
        }),
        ('Specifications', {
            'fields': ('max_passengers', 'cruise_speed_kmh', 'max_range_km')
        }),
        ('Physical Dimensions', {
            'fields': ('cargo_capacity_kg',)
        }),
    )

@admin.register(Aircraft)

# Admin interface for Aircraft model
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('registration', 'model', 'in_service_date', 'is_active')
    list_filter = ('is_active', 'model')
    search_fields = ('registration',)

    fieldsets = (
        (None, {
            'fields': ('registration', 'model', 'is_active')
        }),
        ('Dates', {
            'fields': ('in_service_date',)
        }),
        ('Seating', {
            'fields': ('capacity_economy', 'capacity_premium', 'capacity_business', 'capacity_first')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

@admin.register(Route)

# Admin interface for Route model
class RouteAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'distance_km', 'duration_minutes', 'is_active')
    list_filter = ('origin', 'destination', 'is_active')
    search_fields = ('origin__code', 'origin__name', 'destination__code', 'destination__name')

    fieldsets = (
        (None, {
            'fields': ('origin', 'destination', 'is_active')
        }),
        ('Route Details', {
            'fields': ('distance_km', 'duration_minutes')
        }),
    )

@admin.register(FlightSchedule)

# Admin interface for FlightSchedule model
class FlightScheduleAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'route_display', 'departure_time', 'arrival_time', 'days_display', 'effective_dates', 'is_active')
    list_filter = ('is_active', 'route__origin', 'route__destination', 'operates_monday', 'operates_tuesday', 'operates_wednesday', 
                  'operates_thursday', 'operates_friday', 'operates_saturday', 'operates_sunday')
    search_fields = ('flight_number', 'route__origin__code', 'route__destination__code')
    ordering = ('flight_number',)

    fieldsets = (
        (None, {
            'fields': ('flight_number', 'route', 'aircraft_type', 'is_active')
        }),
        ('Schedule', {
            'fields': ('departure_time', 'arrival_time', 
                       ('operates_monday', 'operates_tuesday', 'operates_wednesday', 
                        'operates_thursday', 'operates_friday', 'operates_saturday', 'operates_sunday'),
                       'effective_from', 'effective_until')
        }),
        ('Pricing', {
            'fields': ('economy_price', 'business_price', 'first_price')
        }),
    )

    def route_display(self, obj):
        return f"{obj.route.origin.code} → {obj.route.destination.code}"
    route_display.short_description = "Route"

    def days_display(self, obj):
        return obj.get_days_display()
    days_display.short_description = "Days of Operation"

    def effective_dates(self, obj):
        if obj.effective_until:
            return f"{obj.effective_from} to {obj.effective_until}"
        return f"From {obj.effective_from}"
    effective_dates.short_description = "Effective Dates"

@admin.register(Flight)

# Admin interface for Flight model
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'route_display', 'scheduled_departure_display', 'status', 'aircraft')
    list_filter = ('status', 'route__origin', 'route__destination', 'scheduled_departure')
    search_fields = ('flight_number', 'route__origin__code', 'route__destination__code')
    date_hierarchy = 'scheduled_departure'

    fieldsets = (
        (None, {
            'fields': ('flight_number', 'route', 'aircraft', 'is_active', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_departure', 'scheduled_arrival', 'actual_departure', 'actual_arrival')
        }),
        ('Flight Details', {
            'fields': ('base_price', 'available_travel_classes')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    actions = ['mark_flight_departed', 'mark_flight_arrived', 'mark_flight_cancelled', 'mark_flight_delayed']

    def route_display(self, obj):
        if obj.route:
            return f"{obj.route.origin.code} → {obj.route.destination.code}"
        return "-"
    route_display.short_description = "Route"

    def scheduled_departure_display(self, obj):
        if obj.scheduled_departure:
            return obj.scheduled_departure.strftime("%Y-%m-%d %H:%M")
        return "-"
    scheduled_departure_display.short_description = "Departure"

    def mark_flight_departed(self, request, queryset):
        for flight in queryset:
            flight.status = 'in_air'
            flight.save()
        self.message_user(request, f"{queryset.count()} flights marked as departed.")
    mark_flight_departed.short_description = "Mark selected flights as departed"

    def mark_flight_arrived(self, request, queryset):
        for flight in queryset:
            flight.status = 'arrived'
            flight.save()
        self.message_user(request, f"{queryset.count()} flights marked as arrived.")
    mark_flight_arrived.short_description = "Mark selected flights as arrived"

    def mark_flight_cancelled(self, request, queryset):
        for flight in queryset:
            flight.status = 'cancelled'
            flight.save()
        self.message_user(request, f"{queryset.count()} flights cancelled.")
    mark_flight_cancelled.short_description = "Cancel selected flights"

    def mark_flight_delayed(self, request, queryset):
        for flight in queryset:
            flight.status = 'delayed'
            flight.save()
        self.message_user(request, f"{queryset.count()} flights delayed.")
    mark_flight_delayed.short_description = "Delay selected flights"
