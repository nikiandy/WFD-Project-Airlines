from django import forms
from django.utils import timezone
from .models import Flight, Aircraft, Airport, Route, TravelClass
from datetime import timedelta

# Form for Flight - collects and validates user input
class FlightForm(forms.ModelForm):

    class Meta:
        model = Flight
        fields = [
            'flight_number', 'route', 'aircraft', 
            'scheduled_departure', 'scheduled_arrival',
            'status', 'base_price', 'is_active', 'notes'
        ]
        widgets = {
            'scheduled_departure': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'scheduled_arrival': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['route'].queryset = Route.objects.filter(is_active=True)

        self.fields['aircraft'].queryset = Aircraft.objects.filter(is_active=True)

        if self.instance and self.instance.pk:
            if self.instance.scheduled_departure:
                self.initial['scheduled_departure'] = self.instance.scheduled_departure.strftime('%Y-%m-%dT%H:%M')
            if self.instance.scheduled_arrival:
                self.initial['scheduled_arrival'] = self.instance.scheduled_arrival.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        scheduled_departure = cleaned_data.get('scheduled_departure')
        scheduled_arrival = cleaned_data.get('scheduled_arrival')

        if scheduled_departure and scheduled_arrival:
            if scheduled_arrival <= scheduled_departure:
                self.add_error('scheduled_arrival', 'Arrival time must be after departure time')

        flight_number = cleaned_data.get('flight_number')
        if flight_number:
            if not flight_number.startswith('SK'):
                self.add_error('flight_number', 'Flight number must start with SK')

        return cleaned_data

# Form for Flightsearch - collects and validates user input
class FlightSearchForm(forms.Form):

    TRIP_TYPE_CHOICES = [
        ('one_way', 'One Way'),
        ('round_trip', 'Round Trip'),
    ]

    trip_type = forms.ChoiceField(
        choices=TRIP_TYPE_CHOICES,
        initial='one_way',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    origin = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'From (Airport code)',
            'data-toggle': 'airport-autocomplete'
        })
    )

    destination = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'To (Airport code or "any")',
            'data-toggle': 'airport-autocomplete'
        })
    )

    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'placeholder': 'Departure date',
            'type': 'date'
        })
    )

    return_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'placeholder': 'Return date (optional)',
            'type': 'date'
        })
    )

    travel_class = forms.ChoiceField(
        choices=[
            ('economy', 'Economy'),
            ('premium_economy', 'Premium Economy'),
            ('business', 'Business'),
            ('first', 'First Class')
        ],
        initial='economy',
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    passengers = forms.IntegerField(
        min_value=1,
        max_value=9,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Passengers'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = timezone.now().date()

        if not self.is_bound:
            self.fields['departure_date'].initial = today + timedelta(days=1)

    def clean(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get('origin')
        destination = cleaned_data.get('destination')
        departure_date = cleaned_data.get('departure_date')
        return_date = cleaned_data.get('return_date')

        if origin and destination and origin.upper() == destination.upper() and destination.upper() != 'ANY':
            self.add_error('destination', 'Origin and destination cannot be the same')

        if departure_date and departure_date < timezone.now().date():
            self.add_error('departure_date', 'Departure date cannot be in the past')

        if return_date and departure_date and return_date < departure_date:
            self.add_error('return_date', 'Return date must be after departure date')

        return cleaned_data 