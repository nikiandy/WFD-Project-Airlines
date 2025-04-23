from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .models import Flight, Aircraft, Airport
from django.views.decorators.csrf import csrf_exempt
import datetime
import sqlite3
import os
from django.conf import settings

def get_db_connection():
    db_path = settings.DATABASES['default']['NAME']
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def simple_flight_management(request):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute()

        flights = cursor.fetchall()
    except Exception as e:
        return HttpResponse(f"Database error: {str(e)}", status=500)
    finally:
        conn.close()

    html = 

    for flight in flights:
        try:

            dep_time = datetime.datetime.fromisoformat(flight['scheduled_departure'])
            formatted_time = dep_time.strftime('%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            formatted_time = "Unknown"

        html += f

    html += 

    return HttpResponse(html)

@csrf_exempt
def simple_flight_create(request):
    if request.method == 'POST':
        flight_number = request.POST.get('flight_number')
        departure_airport_id = int(request.POST.get('departure_airport'))
        arrival_airport_id = int(request.POST.get('arrival_airport'))
        scheduled_departure = request.POST.get('scheduled_departure')
        scheduled_arrival = request.POST.get('scheduled_arrival')
        aircraft_id = int(request.POST.get('aircraft'))
        status = request.POST.get('status', 'scheduled')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(, (
            flight_number, 
            departure_airport_id, 
            arrival_airport_id, 
            scheduled_departure, 
            scheduled_arrival, 
            aircraft_id, 
            status,
            datetime.datetime.now().isoformat(),
            datetime.datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        return HttpResponseRedirect('/flights/simple')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, registration FROM flights_aircraft")
    aircraft_list = cursor.fetchall()

    cursor.execute("SELECT id, code, name FROM flights_airport")
    airport_list = cursor.fetchall()

    conn.close()

    aircraft_options = ""
    for aircraft in aircraft_list:
        aircraft_options += f'<option value="{aircraft["id"]}">{aircraft["registration"]}</option>'

    airport_options = ""
    for airport in airport_list:
        airport_options += f'<option value="{airport["id"]}">{airport["code"]} - {airport["name"]}</option>'

    status_options = ""
    for status_choice in [('scheduled', 'Scheduled'), ('active', 'Active'), ('landed', 'Landed'), ('cancelled', 'Cancelled'), ('delayed', 'Delayed')]:
        status_options += f'<option value="{status_choice[0]}">{status_choice[1]}</option>'

    html = f

    return HttpResponse(html)

@csrf_exempt
def simple_flight_update(request, flight_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        flight_number = request.POST.get('flight_number')
        departure_airport_id = int(request.POST.get('departure_airport'))
        arrival_airport_id = int(request.POST.get('arrival_airport'))
        scheduled_departure = request.POST.get('scheduled_departure')
        scheduled_arrival = request.POST.get('scheduled_arrival')
        aircraft_id = int(request.POST.get('aircraft'))
        status = request.POST.get('status')

        cursor.execute(, (
            flight_number, 
            departure_airport_id, 
            arrival_airport_id, 
            scheduled_departure, 
            scheduled_arrival, 
            aircraft_id, 
            status,
            datetime.datetime.now().isoformat(),
            flight_id
        ))

        conn.commit()
        conn.close()

        return HttpResponseRedirect('/flights/simple')

    cursor.execute(, (flight_id,))

    flight = cursor.fetchone()

    if not flight:
        conn.close()
        return HttpResponse("Flight not found", status=404)

    cursor.execute("SELECT id, registration FROM flights_aircraft")
    aircraft_list = cursor.fetchall()

    cursor.execute("SELECT id, code, name FROM flights_airport")
    airport_list = cursor.fetchall()

    conn.close()

    aircraft_options = ""
    for aircraft in aircraft_list:
        selected = "selected" if aircraft["id"] == flight["aircraft_id"] else ""
        aircraft_options += f'<option value="{aircraft["id"]}" {selected}>{aircraft["registration"]}</option>'

    airport_options_dep = ""
    airport_options_arr = ""
    for airport in airport_list:
        selected_dep = "selected" if airport["id"] == flight["departure_airport_id"] else ""
        airport_options_dep += f'<option value="{airport["id"]}" {selected_dep}>{airport["code"]} - {airport["name"]}</option>'

        selected_arr = "selected" if airport["id"] == flight["arrival_airport_id"] else ""
        airport_options_arr += f'<option value="{airport["id"]}" {selected_arr}>{airport["code"]} - {airport["name"]}</option>'

    status_options = ""
    for status_choice in [('scheduled', 'Scheduled'), ('active', 'Active'), ('landed', 'Landed'), ('cancelled', 'Cancelled'), ('delayed', 'Delayed')]:
        selected = "selected" if status_choice[0] == flight["status"] else ""
        status_options += f'<option value="{status_choice[0]}" {selected}>{status_choice[1]}</option>'

    dep_time = datetime.datetime.fromisoformat(flight['scheduled_departure'])
    arr_time = datetime.datetime.fromisoformat(flight['scheduled_arrival'])

    formatted_dep_time = dep_time.strftime('%Y-%m-%dT%H:%M')
    formatted_arr_time = arr_time.strftime('%Y-%m-%dT%H:%M')

    html = f

    return HttpResponse(html)

@csrf_exempt
def simple_flight_delete(request, flight_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(, (flight_id,))

    flight = cursor.fetchone()

    if not flight:
        conn.close()
        return HttpResponse("Flight not found", status=404)

    if request.method == 'POST':

        cursor.execute("DELETE FROM flights_flight WHERE id = ?", (flight_id,))
        conn.commit()
        conn.close()
        return HttpResponseRedirect('/flights/simple')

    conn.close()

    html = f

    return HttpResponse(html) 