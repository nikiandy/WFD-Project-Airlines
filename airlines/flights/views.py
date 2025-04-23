from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, JsonResponse, Http404
from datetime import datetime, timedelta
from .models import Flight, Aircraft, Airport, Route, FlightSchedule, TravelClass
from .forms import FlightForm, FlightSearchForm
from functools import wraps
import pytz
import random
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, TemplateView

# Decorator to ensure user is a flight manager
def flight_manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_flight_manager():
            return HttpResponseForbidden("You don't have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Check if a user has flight manager permissions
def is_flight_manager(user):
    return user.is_authenticated and (user.is_staff or user.role.lower() == 'planning_manager')

# Homepage view
def index(request):
    search_form = FlightSearchForm()

    featured_destinations = [
        {'code': 'JFK', 'name': 'New York', 'image': 'images/destinations/new-york.jpg'},
        {'code': 'LHR', 'name': 'London', 'image': 'images/destinations/london.jpg'},
        {'code': 'SYD', 'name': 'Sydney', 'image': 'images/destinations/sydney.jpg'},
        {'code': 'DXB', 'name': 'Dubai', 'image': 'images/destinations/dubai.jpg'},
        {'code': 'HND', 'name': 'Tokyo', 'image': 'images/destinations/tokyo.jpg'},
        {'code': 'CDG', 'name': 'Paris', 'image': 'images/destinations/paris.jpg'},
    ]

    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)

    upcoming_flights = Flight.objects.filter(
        scheduled_departure__date__gte=today,
        scheduled_departure__date__lte=next_week,
        status='scheduled'
    ).order_by('scheduled_departure')[:5]

    return render(request, 'flights/index.html', {
        'search_form': search_form,
        'featured_destinations': featured_destinations,
        'upcoming_flights': upcoming_flights,
        'today': today,
        'tomorrow': tomorrow,
    })

@login_required
@user_passes_test(is_flight_manager)
# Flight list management view - shows all flights for admin/manager
def flight_list(request):
    query = request.GET.get('query', '')
    origin = request.GET.get('origin', '')
    destination = request.GET.get('destination', '')
    date = request.GET.get('date', '')
    status = request.GET.get('status', '')

    flights = Flight.objects.all().order_by('-scheduled_departure')

    if query:
        flights = flights.filter(
            Q(flight_number__icontains=query) |
            Q(notes__icontains=query)
        )

    if origin:
        flights = flights.filter(route__origin__code=origin)

    if destination:
        flights = flights.filter(route__destination__code=destination)

    if date:
        try:
            search_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
            flights = flights.filter(scheduled_departure__date=search_date)
        except ValueError:
            pass

    if status:
        flights = flights.filter(status=status)

    paginator = Paginator(flights, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    airports = Airport.objects.filter(is_active=True).order_by('name')

    context = {
        'title': 'Flights Management',
        'page_obj': page_obj,
        'query': query,
        'origin': origin,
        'destination': destination,
        'date': date,
        'status': status,
        'airports': airports,
        'STATUS_CHOICES': Flight.STATUS_CHOICES,
    }

    return render(request, 'flights/flight_list.html', context)

# Flight detail - shows information about a specific flight
def flight_detail(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)

    travel_classes = flight.available_travel_classes.all()

    class_availability = {}
    for travel_class in travel_classes:
        if travel_class.code == 'ECON':
            available = flight.aircraft.economy_seats
        elif travel_class.code == 'PREM':
            available = flight.aircraft.premium_economy_seats
        elif travel_class.code == 'BUS':
            available = flight.aircraft.business_class_seats
        elif travel_class.code == 'FRST':
            available = flight.aircraft.first_class_seats
        else:
            available = 0

        class_availability[travel_class.code] = {
            'name': travel_class.name,
            'available': available,
            'price': flight.get_price_for_class(travel_class.code)
        }

    return render(request, 'flights/flight_detail.html', {
        'title': f'Flight {flight.flight_number}',
        'flight': flight,
        'travel_classes': travel_classes,
        'class_availability': class_availability
    })

# Flight status - displays current flight status
def flight_status(request):
    today = timezone.now().date()

    flight_number = request.GET.get('flight_number', '')
    date_str = request.GET.get('date', '')

    try:
        if date_str:
            search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            search_date = today
    except ValueError:
        search_date = today

    flights = Flight.objects.filter(scheduled_departure__date=search_date)

    if flight_number:
        flights = flights.filter(flight_number__icontains=flight_number)

    flights = flights.order_by('scheduled_departure')

    return render(request, 'flights/flight_status.html', {
        'title': 'Flight Status',
        'flights': flights,
        'flight_number': flight_number,
        'date': search_date.strftime('%Y-%m-%d'),
        'today': today.strftime('%Y-%m-%d')
    })

# Aircraft list - displays all available aircraft
def aircraft_list(request):
    aircraft = Aircraft.objects.all().order_by('fleet_number')

    return render(request, 'flights/aircraft_list.html', {
        'title': 'Aircraft Information',
        'aircraft': aircraft,
    })

# Aircraft detail - shows information about a specific aircraft
def aircraft_detail(request, aircraft_id):
    aircraft = get_object_or_404(Aircraft, pk=aircraft_id)

    upcoming_flights = Flight.objects.filter(
        aircraft=aircraft,
        scheduled_departure__gte=timezone.now()
    ).order_by('scheduled_departure')[:5]

    return render(request, 'flights/aircraft_detail.html', {
        'title': f'Aircraft {aircraft.registration}',
        'aircraft': aircraft,
        'upcoming_flights': upcoming_flights
    })

# Flight search - allows users to find available flights (Use Case: Search Flights)
def flight_search(request):
    form = FlightSearchForm(request.GET or None)
    flights = []
    search_performed = False

    if form.is_valid() and request.GET:
        search_performed = True
        origin = form.cleaned_data.get('origin')
        destination = form.cleaned_data.get('destination')
        departure_date = form.cleaned_data.get('departure_date')
        return_date = form.cleaned_data.get('return_date')
        travel_class = form.cleaned_data.get('travel_class')

        outbound_flights = Flight.objects.filter(
            route__origin=origin,
            route__destination=destination,
            scheduled_departure__date=departure_date,
            is_active=True
        ).exclude(status__in=['CANCELLED', 'DIVERTED'])

        return_flights = []
        if return_date:
            return_flights = Flight.objects.filter(
                route__origin=destination,
                route__destination=origin,
                scheduled_departure__date=return_date,
                is_active=True
            ).exclude(status__in=['CANCELLED', 'DIVERTED'])

        context = {
            'title': 'Flight Search Results',
            'form': form,
            'outbound_flights': outbound_flights,
            'return_flights': return_flights,
            'search_performed': search_performed,
            'travel_class': travel_class
        }

        return render(request, 'flights/search_results.html', context)

    airports = Airport.objects.filter(is_active=True).order_by('name')

    context = {
        'title': 'Search Flights',
        'form': form,
        'airports': airports,
        'search_performed': search_performed
    }

    return render(request, 'flights/search.html', context)

# Generate test flights for demonstration purposes
def generate_flights(request):
    if request.method == 'POST':
        try:
            routes = Route.objects.filter(is_active=True)
            aircraft = Aircraft.objects.filter(is_active=True)

            if not routes or not aircraft:
                messages.error(request, "Cannot generate flights: No active routes or aircraft found.")
                return redirect('flights:index')

            days = int(request.POST.get('days', 30))
            flights_per_day = int(request.POST.get('flights_per_day', 10))

            days = min(max(days, 1), 90)
            flights_per_day = min(max(flights_per_day, 1), 50)

            flights_created = 0

            for day in range(days):
                date = timezone.now().date() + timedelta(days=day)

                for _ in range(flights_per_day):
                    route = random.choice(routes)
                    plane = random.choice(aircraft)

                    hour = random.randint(6, 22)
                    minute = random.choice([0, 15, 30, 45])

                    departure_time = timezone.datetime.combine(
                        date, 
                        timezone.datetime.min.time().replace(hour=hour, minute=minute),
                        tzinfo=timezone.get_current_timezone()
                    )

                    duration_minutes = route.duration_minutes or 120
                    arrival_time = departure_time + timedelta(minutes=duration_minutes)

                    flight_number = f"SK{route.code}{random.randint(1000, 9999)}"

                    base_price = (route.distance_km or 1000) * 0.10 + random.randint(-50, 50)
                    base_price = max(base_price, 50)

                    try:
                        flight = Flight.objects.create(
                            flight_number=flight_number,
                            route=route,
                            aircraft=plane,
                            scheduled_departure=departure_time,
                            scheduled_arrival=arrival_time,
                            status='SCHEDULED',
                            base_price=base_price,
                            is_active=True,
                            notes=f"Auto-generated flight for {date}",
                        )
                        flights_created += 1
                    except Exception as e:
                        continue

            messages.success(request, f"Successfully generated {flights_created} flights over {days} days.")

        except Exception as e:
            messages.error(request, f"Error generating flights: {str(e)}")

        return redirect('flights:index')

    return render(request, 'flights/generate_flights.html', {
        'title': 'Generate Flights'
    })

@flight_manager_required
# Flight management - admin interface for flight operations
def flight_management(request):
    today = timezone.now().date()
    end_date = today + timedelta(days=30)

    flights = Flight.objects.filter(
        scheduled_departure__date__gte=today,
        scheduled_departure__date__lte=end_date
    ).order_by('scheduled_departure')

    total_flights = flights.count()
    scheduled_flights = flights.filter(status='scheduled').count()
    cancelled_flights = flights.filter(status='cancelled').count()
    delayed_flights = flights.filter(status='delayed').count()

    return render(request, 'flights/flight_management.html', {
        'title': 'Flight Management',
        'flights': flights[:20],
        'today': today,
        'end_date': end_date,
        'total_flights': total_flights,
        'scheduled_flights': scheduled_flights,
        'cancelled_flights': cancelled_flights,
        'delayed_flights': delayed_flights
    })

@login_required
@user_passes_test(is_flight_manager)
# CREATE operation - adds a new flight to the system
def flight_create(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            flight = form.save(commit=False)
            flight.created_by = request.user
            flight.updated_by = request.user
            flight.save()
            form.save_m2m()

            messages.success(request, f'Flight {flight.flight_number} has been created successfully!')
            return redirect('flights:flight_detail', pk=flight.pk)
    else:
        form = FlightForm(initial={'status': 'SCHEDULED'})

    context = {
        'form': form,
        'flight': None,
    }

    return render(request, 'flights/flight_form.html', context)

@login_required
@user_passes_test(is_flight_manager)
# UPDATE operation - modifies an existing flight
def flight_edit(request, pk):
    flight = get_object_or_404(Flight, pk=pk)

    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            flight = form.save(commit=False)
            flight.updated_by = request.user
            flight.updated_at = timezone.now()
            flight.save()
            form.save_m2m()

            messages.success(request, f'Flight {flight.flight_number} has been updated successfully!')
            return redirect('flights:flight_detail', pk=flight.pk)
    else:
        form = FlightForm(instance=flight)

    context = {
        'form': form,
        'flight': flight,
    }

    return render(request, 'flights/flight_form.html', context)

@login_required
@user_passes_test(is_flight_manager)
# DELETE operation - removes a flight from the system
def flight_delete(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    
    if request.method == 'POST':
        flight_number = flight.flight_number
        flight.delete()
        messages.success(request, f'Flight {flight_number} has been deleted successfully!')
        return redirect('flights:flight_list')
    
    return render(request, 'flights/flight_delete.html', {
        'flight': flight
    })

@login_required
@user_passes_test(is_flight_manager)

def flight_update(
    return flight_edit(request, flight_id)

def api_search_flights(
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    departure_date = request.GET.get('departure_date')
    travel_class = request.GET.get('travel_class')

    if not all([origin, destination, departure_date]):
        return JsonResponse({
            'success': False,
            'message': 'Missing required parameters',
            'required': ['origin', 'destination', 'departure_date']
        })

    try:
        departure_date = timezone.datetime.strptime(departure_date, '%Y-%m-%d').date()

        flights = Flight.objects.filter(
            route__origin__code=origin,
            route__destination__code=destination,
            scheduled_departure__date=departure_date,
            is_active=True
        ).exclude(status__in=['CANCELLED', 'DIVERTED'])

        flight_data = []
        for flight in flights:
            price = flight.base_price
            if travel_class == 'business':
                price *= 2.5
            elif travel_class == 'first':
                price *= 4

            flight_data.append({
                'id': flight.id,
                'flight_number': flight.flight_number,
                'origin': {
                    'code': flight.route.origin.code,
                    'name': flight.route.origin.name,
                    'city': flight.route.origin.city,
                    'country': flight.route.origin.country
                },
                'destination': {
                    'code': flight.route.destination.code,
                    'name': flight.route.destination.name,
                    'city': flight.route.destination.city,
                    'country': flight.route.destination.country
                },
                'departure': flight.scheduled_departure.isoformat(),
                'arrival': flight.scheduled_arrival.isoformat(),
                'duration': flight.duration_minutes,
                'aircraft': flight.aircraft.registration,
                'aircraft_type': flight.aircraft.aircraft_type.name,
                'status': flight.status,
                'price': round(price, 2)
            })

        return JsonResponse({
            'success': True,
            'count': len(flight_data),
            'flights': flight_data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

# Flightsearch view
class FlightSearchView(TemplateView):
    template_name = 'flights/flight_search.html'

        context = super().get_context_data(**kwargs)
        context['airports'] = Airport.objects.filter(is_active=True).order_by('city', 'name')
        return context

# Flightsearchresults view
class FlightSearchResultsView(ListView):
    model = Flight
    template_name = 'flights/flight_search_results.html'
    context_object_name = 'flights'

        origin = self.request.GET.get('origin')
        destination = self.request.GET.get('destination')
        departure_date_str = self.request.GET.get('departure_date')

        if not (origin and destination and departure_date_str):
            return Flight.objects.none()

        try:
            departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Flight.objects.none()

        departure_start = timezone.make_aware(datetime.combine(departure_date, datetime.min.time()))
        departure_end = timezone.make_aware(datetime.combine(departure_date, datetime.max.time()))

        return Flight.objects.filter(
            route__origin__code=origin,
            route__destination__code=destination,
            scheduled_departure__gte=departure_start,
            scheduled_departure__lte=departure_end,
            status__in=['scheduled', 'boarding', 'delayed'],
            is_active=True
        ).select_related('route', 'route__origin', 'route__destination', 'aircraft', 'aircraft__aircraft_type')

        context = super().get_context_data(**kwargs)
        origin = self.request.GET.get('origin')
        destination = self.request.GET.get('destination')
        departure_date = self.request.GET.get('departure_date')

        origin_airport = Airport.objects.filter(code=origin).first() if origin else None
        destination_airport = Airport.objects.filter(code=destination).first() if destination else None

        context.update({
            'origin': origin_airport,
            'destination': destination_airport,
            'departure_date': departure_date,
            'travel_classes': self.request.GET.getlist('travel_class')
        })

        return context

# Flightdetail view
class FlightDetailView(DetailView):
    model = Flight
    template_name = 'flights/flight_detail.html'
    context_object_name = 'flight'

        flight_number = self.kwargs.get('flight_number')
        departure_date_str = self.kwargs.get('departure_date')
        departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').date()

        departure_start = timezone.make_aware(datetime.combine(departure_date, datetime.min.time()))
        departure_end = timezone.make_aware(datetime.combine(departure_date, datetime.max.time()))

        return get_object_or_404(
            Flight.objects.select_related('route', 'route__origin', 'route__destination', 'aircraft'),
            flight_number=flight_number,
            scheduled_departure__gte=departure_start,
            scheduled_departure__lte=departure_end
        )

        context = super().get_context_data(**kwargs)
        flight = self.get_object()

        context['available_classes'] = flight.available_travel_classes.all()

        return context

def airport_autocomplete(
    query = request.GET.get('q', '')

    if len(query) < 2:
        return JsonResponse({'results': []})

    airports = Airport.objects.filter(
        Q(code__icontains=query) | 
        Q(name__icontains=query) | 
        Q(city__icontains=query)
    ).filter(is_active=True)[:10]

    results = [{
        'code': airport.code,
        'name': airport.name,
        'city': airport.city,
        'country': airport.country,
        'label': f"{airport.city} ({airport.code}) - {airport.name}"
    } for airport in airports]

    return JsonResponse({'results': results})

# Flightstatus view
class FlightStatusView(TemplateView):
    template_name = 'flights/flight_status.html'

        context = super().get_context_data(**kwargs)
        now = timezone.now()

        departures = Flight.objects.filter(
            scheduled_departure__gte=now - timedelta(hours=1),
            scheduled_departure__lte=now + timedelta(hours=12),
            status__in=['scheduled', 'boarding', 'delayed']
        ).order_by('scheduled_departure')[:20]

        arrivals = Flight.objects.filter(
            scheduled_arrival__gte=now - timedelta(hours=1),
            scheduled_arrival__lte=now + timedelta(hours=6),
            status__in=['in_air', 'arrived', 'delayed', 'departed']
        ).order_by('scheduled_arrival')[:20]

        context.update({
            'departures': departures,
            'arrivals': arrivals,
            'now': now
        })

        return context

# Home view
class HomeView(TemplateView):
    template_name = 'flights/home.html'

        context = super().get_context_data(**kwargs)

        context['airports'] = Airport.objects.filter(is_active=True).order_by('city', 'name')

        now = timezone.now()
        upcoming_flights = Flight.objects.filter(
            scheduled_departure__gte=now,
            scheduled_departure__lte=now + timedelta(days=7),
            status__in=['scheduled', 'boarding', 'delayed'],
            is_active=True
        ).order_by('scheduled_departure')[:6]

        context['upcoming_flights'] = upcoming_flights

        featured_routes = Route.objects.filter(is_active=True).order_by('?')[:4]
        context['featured_routes'] = featured_routes

        return context

def flight_search_api(
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    departure_date_str = request.GET.get('departure_date')

    if not (origin and destination and departure_date_str):
        return JsonResponse({'error': 'Missing required parameters'}, status=400)

    try:
        departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    departure_start = timezone.make_aware(datetime.combine(departure_date, datetime.min.time()))
    departure_end = timezone.make_aware(datetime.combine(departure_date, datetime.max.time()))

    flights = Flight.objects.filter(
        route__origin__code=origin,
        route__destination__code=destination,
        scheduled_departure__gte=departure_start,
        scheduled_departure__lte=departure_end,
        status__in=['scheduled', 'boarding', 'delayed'],
        is_active=True
    ).select_related('route', 'route__origin', 'route__destination', 'aircraft')

    results = []
    for flight in flights:
        results.append({
            'flight_number': flight.flight_number,
            'origin': flight.route.origin.code,
            'destination': flight.route.destination.code,
            'departure_time': flight.scheduled_departure.strftime('%H:%M'),
            'arrival_time': flight.scheduled_arrival.strftime('%H:%M'),
            'duration': flight.duration_minutes,
            'status': flight.status,
            'aircraft': flight.aircraft.aircraft_type.name if flight.aircraft else 'TBA',
            'base_price': float(flight.base_price)
        })

    return JsonResponse({'flights': results})

def flight_schedule_generate_api(
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    date_str = request.GET.get('date')

    if not (origin and destination and date_str):
        return JsonResponse({'error': 'Missing required parameters'}, status=400)

    try:
        search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    day_of_week = search_date.weekday()
    day_filter = {
        0: 'operates_monday',
        1: 'operates_tuesday',
        2: 'operates_wednesday', 
        3: 'operates_thursday',
        4: 'operates_friday',
        5: 'operates_saturday',
        6: 'operates_sunday'
    }[day_of_week]

    schedules = FlightSchedule.objects.filter(
        route__origin__code=origin,
        route__destination__code=destination,
        effective_from__lte=search_date,
        **{day_filter: True},
        is_active=True
    ).select_related('route', 'route__origin', 'route__destination', 'aircraft_type')

    if schedules.exists():
        return JsonResponse({'schedules_found': True})
    else:
        return JsonResponse({'schedules_found': False})

def route_search(
    origin = request.GET.get('origin')

    if not origin or len(origin) < 3:
        return JsonResponse({'results': []})

    routes = Route.objects.filter(
        origin__code=origin,
        is_active=True
    ).select_related('destination')

    results = [{
        'origin': route.origin.code,
        'destination': route.destination.code,
        'destination_city': route.destination.city,
        'destination_name': route.destination.name,
    } for route in routes]

    return JsonResponse({'results': results})
