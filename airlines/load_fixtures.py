import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airlines.settings')
django.setup()

from django.core.management import call_command
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.db import transaction
from flights.models import Flight, FlightSchedule, Airport, AircraftType, Aircraft, Route, TravelClass
import pytz

def load_fixtures():
    print("Loading fixtures...")

    print("Loading airports...")
    call_command('loaddata', 'fixtures/airports.json', verbosity=2)

    print("Loading aircraft types...")
    call_command('loaddata', 'fixtures/aircraft_types.json', verbosity=2)

    print("Loading aircraft...")
    call_command('loaddata', 'fixtures/aircraft.json', verbosity=2)

    print("Loading routes...")
    call_command('loaddata', 'fixtures/routes.json', verbosity=2)

    print("Loading travel classes...")
    call_command('loaddata', 'fixtures/travel_classes.json', verbosity=2)

    print("Loading flight schedules...")
    call_command('loaddata', 'fixtures/flight_schedules.json', verbosity=2)

    print("All fixtures loaded successfully!")

def generate_flights():
    print("Generating flights for the next 7 days...")

    today = timezone.now().date()
    end_date = today + timedelta(days=7)
    days_generated = 0
    flights_created = 0

    current_date = today
    while current_date <= end_date:

        day_of_week = str(current_date.isoweekday())

        schedules = FlightSchedule.objects.filter(
            is_active=True,
            effective_from__lte=current_date,
            days_of_operation__contains=day_of_week
        )

        print(f"Processing {schedules.count()} schedules for {current_date}...")

        for schedule in schedules:

            if schedule.effective_until and current_date > schedule.effective_until:
                continue

            departure_time = datetime.combine(current_date, schedule.departure_time)

            origin_tz = pytz.timezone(schedule.route.origin.timezone)

            departure_time = timezone.make_aware(departure_time, origin_tz)

            arrival_time = departure_time + timedelta(minutes=schedule.route.duration_minutes)

            existing_flight = Flight.objects.filter(
                flight_number=schedule.flight_number,
                scheduled_departure__date=current_date
            ).exists()

            if not existing_flight:

                aircraft = Aircraft.objects.filter(
                    aircraft_type=schedule.aircraft_type,
                    status='active'
                ).first()

                if aircraft:
                    try:
                        with transaction.atomic():

                            flight = Flight.objects.create(
                                flight_number=schedule.flight_number,
                                schedule=schedule,
                                origin=schedule.route.origin,
                                destination=schedule.route.destination,
                                scheduled_departure=departure_time,
                                scheduled_arrival=arrival_time,
                                aircraft=aircraft,
                                status='scheduled',
                                available_seats=aircraft.total_capacity(),
                                booked_seats=0,
                                gate_departure='TBD',
                                gate_arrival='TBD',
                                terminal_departure='TBD',
                                terminal_arrival='TBD'
                            )

                            for travel_class in schedule.available_travel_classes.all():
                                flight.available_travel_classes.add(travel_class)

                            flights_created += 1
                            print(f"Created flight {flight.flight_number} from {flight.origin.code} to {flight.destination.code} on {flight.scheduled_departure.date()}")
                    except Exception as e:
                        print(f"Error creating flight: {str(e)}")

        current_date += timedelta(days=1)
        days_generated += 1

    print(f"Generated {flights_created} flights over {days_generated} days!")

if __name__ == "__main__":
    load_fixtures()
    generate_flights()
    print("Done!") 