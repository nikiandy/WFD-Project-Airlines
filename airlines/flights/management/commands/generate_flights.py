from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from flights.models import Flight, Airport, TravelClass, Route, Aircraft, FlightSchedule
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Generates flight data for the upcoming days'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7, help='Number of days to generate flights for')
        parser.add_argument('--clear', action='store_true', help='Clear existing flights before generating new ones')
        parser.add_argument('--routes', type=int, default=0, help='Number of routes to generate flights for (0 for all)')

    def handle(self, *args, **options):
        days = options['days']
        clear_existing = options['clear']
        routes_limit = options['routes']

        self.stdout.write(self.style.SUCCESS(f'Generating flights for the next {days} days...'))

        routes = Route.objects.filter(is_active=True)
        if routes_limit > 0:
            routes = routes[:routes_limit]

        if not routes.exists():
            raise CommandError('No active routes found in the database.')

        travel_classes = TravelClass.objects.filter(is_active=True)
        if not travel_classes.exists():
            raise CommandError('No active travel classes found in the database.')

        aircraft = Aircraft.objects.filter(status='active')
        if not aircraft.exists():
            raise CommandError('No active aircraft found in the database.')

        if clear_existing:

            today = timezone.now().date()
            flights_to_delete = Flight.objects.filter(scheduled_departure__date__gte=today)
            count = flights_to_delete.count()
            flights_to_delete.delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing flights.'))

        total_flights = 0
        today = timezone.now().date()

        for day_offset in range(days):
            flight_date = today + timedelta(days=day_offset)

            day_flights = 0

            for route in routes:

                flight_times = [
                    {'departure': 8, 'duration': route.duration_minutes},
                    {'departure': 13, 'duration': route.duration_minutes},
                    {'departure': 18, 'duration': route.duration_minutes}
                ]

                for time_slot in flight_times:

                    departure_hour = time_slot['departure']
                    duration_minutes = time_slot['duration']

                    departure_hour += random.randint(-1, 1)
                    departure_minute = random.randint(0, 59)

                    departure_time = timezone.make_aware(
                        datetime.combine(
                            flight_date, 
                            datetime.min.time().replace(hour=departure_hour, minute=departure_minute)
                        )
                    )
                    arrival_time = departure_time + timedelta(minutes=duration_minutes)

                    flight_number = f"SK{route.code}{day_offset % 7 + 1}"

                    random_aircraft = random.choice(aircraft)

                    flight = Flight.objects.create(
                        flight_number=flight_number,
                        origin=route.origin,
                        destination=route.destination,
                        scheduled_departure=departure_time,
                        scheduled_arrival=arrival_time,
                        aircraft=random_aircraft,
                        status='scheduled',
                        available_seats=random_aircraft.total_capacity(),
                        booked_seats=0
                    )

                    for travel_class in travel_classes:
                        flight.available_travel_classes.add(travel_class)

                    day_flights += 1
                    total_flights += 1

            self.stdout.write(f'Generated {day_flights} flights for {flight_date.strftime("%Y-%m-%d")}')

        self.stdout.write(self.style.SUCCESS(f'Successfully generated {total_flights} flights for {days} days.')) 