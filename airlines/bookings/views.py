from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking, Passenger, Payment
from flights.models import Flight, Airport, TravelClass
import random
import string
import json
from django.db import connection

# Constants for booking status values
class BookingStatus:
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'

# Bookings home page showing list of user's bookings with filtering
def index(request):
    bookings = []
    if request.user.is_authenticated:
        bookings_list = Booking.objects.filter(user=request.user).order_by('-created_at')

        if request.GET.get('status'):
            bookings_list = bookings_list.filter(status=request.GET.get('status'))

        if request.GET.get('date_from'):
            try:
                date_from = datetime.strptime(request.GET.get('date_from'), '%Y-%m-%d')
                bookings_list = bookings_list.filter(created_at__gte=date_from)
            except ValueError:
                pass

        if request.GET.get('date_to'):
            try:
                date_to = datetime.strptime(request.GET.get('date_to'), '%Y-%m-%d')
                bookings_list = bookings_list.filter(created_at__lte=date_to)
            except ValueError:
                pass

        paginator = Paginator(bookings_list, 10)  
        page = request.GET.get('page')
        bookings = paginator.get_page(page)

    context = {
        'bookings': bookings,
    }
    return render(request, 'bookings/index.html', context)

@login_required
# List all bookings for the current user
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'bookings': bookings,
        'title': 'My Bookings'
    }
    return render(request, 'bookings/booking_list.html', context)

@login_required
# Booking detail - shows booking information (Use Case: View Booking)
def booking_detail(request, reference_number):
    booking = get_object_or_404(Booking, reference_number=reference_number)

    if request.user.is_authenticated and booking.user and booking.user != request.user:
        messages.error(request, 'You are not authorized to view this booking')
        return redirect('bookings:index')

    from passengers.models import PassengerBooking
    passenger_bookings = PassengerBooking.objects.filter(booking=booking)

    context = {
        'booking': booking,
        'passenger_bookings': passenger_bookings,
    }
    return render(request, 'bookings/booking_detail.html', context)

# Booking creation - creates a new booking (Use Case: Reserve Flight)
def booking_create(request):
    airports = Airport.objects.values('code', 'name', 'city', 'is_active').filter(is_active=True).order_by('name')
    travel_classes = TravelClass.objects.filter(is_active=True).order_by('display_order')
    today = timezone.now().date()

    if request.method == 'POST':
        try:
            # Get flight and travel class selection
            selected_flight_id = request.POST.get('selected_flight')
            flight = Flight.objects.get(id=selected_flight_id)
            travel_class_code = request.POST.get('travel_class')
            travel_class = TravelClass.objects.get(code=travel_class_code)

            # Generate unique reference number
            reference_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            while Booking.objects.filter(reference_number=reference_number).exists():
                reference_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

            # Create initial booking record
            booking = Booking.objects.create(
                reference_number=reference_number,
                user=request.user if request.user.is_authenticated else None,
                status=BookingStatus.PENDING,
                contact_email=request.POST.get('contact_email'),
                contact_phone=request.POST.get('contact_phone'),
                total_amount=0  
            )

            # Process passenger information
            adult_count = int(request.POST.get('adult_count', 1))
            child_count = int(request.POST.get('child_count', 0))
            total_passengers = adult_count + child_count

            base_price = flight.get_price_for_class(travel_class_code)

            total_amount = 0

            passengers = []
            for i in range(1, total_passengers + 1):
                # Create passenger record for each traveler
                passenger = Passenger.objects.create(
                    first_name=request.POST.get(f'passenger{i}_first_name'),
                    last_name=request.POST.get(f'passenger{i}_last_name'),
                    date_of_birth=request.POST.get(f'passenger{i}_dob'),
                    gender=request.POST.get(f'passenger{i}_gender', 'prefer_not_to_say'),
                    email=request.POST.get('contact_email'),  
                    phone=request.POST.get('contact_phone'),  
                    passport_number=request.POST.get(f'passenger{i}_passport', ''),
                    passport_expiry=request.POST.get(f'passenger{i}_passport_expiry', None),
                    nationality=request.POST.get(f'passenger{i}_nationality', ''),
                    special_assistance=request.POST.get(f'passenger{i}_special_assistance', False) == 'on',
                    special_requirements=request.POST.get(f'passenger{i}_special_requirements', ''),
                    dietary_requirements=request.POST.get(f'passenger{i}_dietary', '')
                )
                passengers.append(passenger)

                booking.passengers.add(passenger)

                total_amount += base_price

            # Process add-on services
            has_priority_boarding = request.POST.get('priority_boarding') == 'on'
            has_extra_baggage = request.POST.get('extra_baggage') == 'on'
            has_travel_insurance = request.POST.get('travel_insurance') == 'on'
            has_premium_meal = request.POST.get('premium_meal') == 'on'

            addon_cost = 0
            if has_priority_boarding:
                addon_cost += 15 * total_passengers
            if has_extra_baggage:
                addon_cost += 35 * total_passengers
            if has_travel_insurance:
                addon_cost += 25 * total_passengers
            if has_premium_meal:
                addon_cost += 20 * total_passengers

            booking.extra_baggage = has_extra_baggage
            booking.has_priority_boarding = has_priority_boarding
            booking.has_travel_insurance = has_travel_insurance
            booking.has_premium_meal = has_premium_meal

            # Calculate taxes and total price
            tax_amount = total_amount * 0.15

            booking.base_amount = total_amount
            booking.tax_amount = tax_amount
            booking.additional_services_amount = addon_cost
            booking.total_amount = total_amount + tax_amount + addon_cost
            booking.save()

            # Create passenger booking relationships
            from passengers.models import PassengerBooking
            for passenger in passengers:
                PassengerBooking.objects.create(
                    booking=booking,
                    passenger=passenger,
                    flight=flight,
                    booking_reference=booking.reference_number,
                    booking_date=timezone.now(),
                    booking_status=BookingStatus.PENDING,
                    seat_preference=request.POST.get('seat_preference', 'no_preference'),
                    base_fare=base_price,
                    taxes=base_price * 0.15,
                    total_amount=base_price * 1.15  
                )

            # Process payment information
            payment_method = request.POST.get('payment_method')

            payment = Payment.objects.create(
                booking=booking,
                payment_method=payment_method,
                status='pending',
                amount=booking.total_amount,
                transaction_id=f"TX-{booking.reference_number}"
            )

            return redirect('bookings:booking_payment', booking.reference_number)

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'bookings/booking_create.html', {
                'airports': airports,
                'travel_classes': travel_classes,
                'today': today
            })

    return render(request, 'bookings/booking_create.html', {
        'airports': airports,
        'travel_classes': travel_classes,
        'today': today
    })

def api_search_flights(request):
    if request.method == 'GET':
        origin = request.GET.get('origin')
        destination = request.GET.get('destination')
        departure_date = request.GET.get('departure_date')
        travel_class = request.GET.get('travel_class')

        if not all([origin, destination, departure_date]):
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

        try:
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()

            cursor = connection.cursor()

            query = """
                SELECT f.id, f.flight_number, f.scheduled_departure, f.scheduled_arrival, f.status,
                       o.code as origin_code, o.name as origin_name, o.city as origin_city,
                       d.code as dest_code, d.name as dest_name, d.city as dest_city,
                       a.model as aircraft_name,
                       (SELECT COUNT(*) FROM bookings_booking_passengers bp 
                        JOIN bookings_booking b ON bp.booking_id = b.id 
                        WHERE b.flight_id = f.id) as booked_seats,
                       CASE
                           WHEN a.aircraft_type = 'narrow_body' THEN 150
                           WHEN a.aircraft_type = 'wide_body' THEN 250
                           ELSE 100
                       END as available_seats
                FROM flights_flight f
                JOIN flights_route r ON f.route_id = r.id
                JOIN flights_airport o ON r.origin_id = o.id
                JOIN flights_airport d ON r.destination_id = d.id
                JOIN flights_aircraft a ON f.aircraft_id = a.id
                WHERE o.code = %s AND d.code = %s 
                AND DATE(f.scheduled_departure) = %s
                AND f.is_active = 1
                AND f.status NOT IN ('CANCELLED', 'DIVERTED')
            """

            cursor.execute(query, [origin, destination, departure_date])
            columns = [col[0] for col in cursor.description]
            flight_rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            flight_data = []
            for flight in flight_rows:
                if travel_class:
                    base_price = 200 if travel_class == 'economy' else 400
                else:
                    base_price = 200

                departure = datetime.fromisoformat(flight['scheduled_departure']) if isinstance(flight['scheduled_departure'], str) else flight['scheduled_departure']
                arrival = datetime.fromisoformat(flight['scheduled_arrival']) if isinstance(flight['scheduled_arrival'], str) else flight['scheduled_arrival']

                duration = int((arrival - departure).total_seconds() / 60)

                flight_data.append({
                    'id': flight['id'],
                    'flight_number': flight['flight_number'],
                    'origin': {
                        'code': flight['origin_code'],
                        'name': flight['origin_name'],
                        'city': flight['origin_city']
                    },
                    'destination': {
                        'code': flight['dest_code'],
                        'name': flight['dest_name'],
                        'city': flight['dest_city']
                    },
                    'departure': departure.isoformat(),
                    'arrival': arrival.isoformat(),
                    'duration_minutes': duration,
                    'aircraft': flight['aircraft_name'],
                    'price': float(base_price),
                    'available_seats': flight['available_seats'] - flight['booked_seats'],
                    'status': flight['status']
                })

            return JsonResponse({'flights': flight_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
# UPDATE operation - allows users to edit their booking (Use Case: Modify Booking)
def booking_edit(request, reference_number):
    booking = get_object_or_404(Booking, reference_number=reference_number)

    if booking.user != request.user:
        messages.error(request, 'You are not authorized to edit this booking')
        return redirect('bookings:index')

    if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
        messages.error(request, f'Bookings with status "{booking.get_status_display()}" cannot be edited')
        return redirect('bookings:booking_detail', reference_number=reference_number)

    from passengers.models import PassengerBooking
    passenger_bookings = PassengerBooking.objects.filter(booking=booking)

    if request.method == 'POST':
        try:
            # Update contact information
            booking.contact_email = request.POST.get('contact_email')
            booking.contact_phone = request.POST.get('contact_phone')

            # Update addon services
            has_priority_boarding = request.POST.get('priority_boarding') == 'on'
            has_extra_baggage = request.POST.get('extra_baggage') == 'on'
            has_travel_insurance = request.POST.get('travel_insurance') == 'on'
            has_premium_meal = request.POST.get('premium_meal') == 'on'

            old_addon_cost = booking.additional_services_amount
            new_addon_cost = 0
            total_passengers = booking.passengers.count()

            if has_priority_boarding:
                new_addon_cost += 15 * total_passengers
            if has_extra_baggage:
                new_addon_cost += 35 * total_passengers
            if has_travel_insurance:
                new_addon_cost += 25 * total_passengers
            if has_premium_meal:
                new_addon_cost += 20 * total_passengers

            booking.extra_baggage = has_extra_baggage
            booking.has_priority_boarding = has_priority_boarding
            booking.has_travel_insurance = has_travel_insurance
            booking.has_premium_meal = has_premium_meal

            # Recalculate total with new addons
            booking.additional_services_amount = new_addon_cost
            booking.total_amount = booking.total_amount - old_addon_cost + new_addon_cost
            booking.save()

            # Update passenger information
            for i, pb in enumerate(passenger_bookings):
                passenger = pb.passenger
                passenger.first_name = request.POST.get(f'passenger{i+1}_first_name')
                passenger.last_name = request.POST.get(f'passenger{i+1}_last_name')
                passenger.special_requirements = request.POST.get(f'passenger{i+1}_special_requirements', '')
                passenger.dietary_requirements = request.POST.get(f'passenger{i+1}_dietary', '')
                passenger.save()

            messages.success(request, 'Booking updated successfully')
            return redirect('bookings:booking_detail', reference_number=reference_number)

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    context = {
        'booking': booking,
        'passenger_bookings': passenger_bookings,
    }
    return render(request, 'bookings/booking_edit.html', context)

@login_required
# Booking cancellation - allows users to cancel bookings (Use Case: Cancel Booking)
def booking_cancel(request, reference_number):
    booking = get_object_or_404(Booking, reference_number=reference_number)

    if booking.user != request.user:
        messages.error(request, 'You are not authorized to cancel this booking')
        return redirect('bookings:index')

    if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
        messages.error(request, f'Bookings with status "{booking.get_status_display()}" cannot be cancelled')
        return redirect('bookings:booking_detail', reference_number=reference_number)

    if request.method == 'POST':
        reason = request.POST.get('cancellation_reason', '')

        # Update booking status to cancelled
        booking.status = BookingStatus.CANCELLED
        booking.save()

        # Update passenger bookings status
        from passengers.models import PassengerBooking
        PassengerBooking.objects.filter(booking=booking).update(booking_status=BookingStatus.CANCELLED)

        # Process refund if already paid
        if booking.payment_status == 'paid':
            payment = booking.payment
            payment.status = 'refunded'
            payment.save()

            booking.payment_status = 'refunded'
            booking.save()

        messages.success(request, 'Booking cancelled successfully')
        return redirect('bookings:booking_detail', reference_number=reference_number)

    context = {
        'booking': booking,
    }
    return render(request, 'bookings/booking_cancel.html', context)

@login_required
# Payment processing - handles booking payment (Use Case: Pay for Booking)
def booking_payment(request, reference_number):
    booking = get_object_or_404(Booking, reference_number=reference_number)

    if booking.user and booking.user != request.user:
        messages.error(request, 'You are not authorized to pay for this booking')
        return redirect('bookings:index')

    if booking.payment_status == 'paid':
        messages.info(request, 'This booking has already been paid for')
        return redirect('bookings:booking_detail', reference_number=reference_number)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        card_number = request.POST.get('card_number', '')
        expiry_date = request.POST.get('expiry_date', '')
        cvv = request.POST.get('cvv', '')

        if payment_method == 'credit_card' and (not card_number or not expiry_date or not cvv):
            messages.error(request, 'Please provide all credit card details')
            return redirect('bookings:booking_payment', reference_number=reference_number)

        # Process payment
        payment = Payment.objects.get(booking=booking)
        payment.payment_method = payment_method
        payment.status = 'completed'
        payment.save()

        # Update booking status after successful payment
        booking.payment_status = 'paid'
        booking.status = BookingStatus.CONFIRMED
        booking.save()

        # Update passenger booking statuses
        from passengers.models import PassengerBooking
        PassengerBooking.objects.filter(booking=booking).update(
            booking_status=BookingStatus.CONFIRMED,
            payment_status='paid'
        )

        messages.success(request, 'Payment processed successfully')
        return redirect('bookings:booking_detail', reference_number=reference_number)

    context = {
        'booking': booking,
    }
    return render(request, 'bookings/booking_payment.html', context)

@login_required
# Manage additional services for an existing booking
def manage_additional_services(request, booking_reference):
    booking = get_object_or_404(Booking, reference_number=booking_reference)

    if booking.user != request.user:
        messages.error(request, 'You are not authorized to manage this booking')
        return redirect('bookings:index')

    if request.method == 'POST':
        has_priority_boarding = request.POST.get('priority_boarding') == 'on'
        has_extra_baggage = request.POST.get('extra_baggage') == 'on'
        has_travel_insurance = request.POST.get('travel_insurance') == 'on'
        has_premium_meal = request.POST.get('premium_meal') == 'on'

        old_additional_amount = booking.additional_services_amount
        new_additional_amount = 0

        passenger_count = booking.passengers.count()

        if has_priority_boarding:
            new_additional_amount += 15 * passenger_count
        if has_extra_baggage:
            new_additional_amount += 35 * passenger_count
        if has_travel_insurance:
            new_additional_amount += 25 * passenger_count
        if has_premium_meal:
            new_additional_amount += 20 * passenger_count

        price_difference = new_additional_amount - old_additional_amount

        booking.has_priority_boarding = has_priority_boarding
        booking.extra_baggage = has_extra_baggage
        booking.has_travel_insurance = has_travel_insurance
        booking.has_premium_meal = has_premium_meal
        booking.additional_services_amount = new_additional_amount
        booking.total_amount = booking.total_amount + price_difference
        booking.save()

        if price_difference > 0:
            return redirect('bookings:booking_payment', reference_number=booking_reference)

        messages.success(request, 'Additional services updated successfully')
        return redirect('bookings:booking_detail', reference_number=booking_reference)

    context = {
        'booking': booking,
    }
    return render(request, 'bookings/manage_services.html', context)
