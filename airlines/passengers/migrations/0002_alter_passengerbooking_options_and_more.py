

import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_alter_booking_options_remove_booking_booking_date_and_more'),
        ('flights', '0002_flightclass'),
        ('passengers', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='passengerbooking',
            options={'verbose_name': 'Passenger Booking', 'verbose_name_plural': 'Passenger Bookings'},
        ),
        migrations.AlterUniqueTogether(
            name='passengerbooking',
            unique_together={('booking', 'passenger', 'flight')},
        ),
        migrations.AddField(
            model_name='passengerbooking',
            name='baggage_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='passengerbooking',
            name='boarded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='passengerbooking',
            name='booking',
            field=models.ForeignKey(default='OLD000001', on_delete=django.db.models.deletion.CASCADE, related_name='passenger_bookings', to='bookings.booking'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='passengerbooking',
            name='carry_on_baggage',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='passengerbooking',
            name='checked_baggage',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='passengerbooking',
            name='checked_in',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='passengerbooking',
            name='extra_baggage',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='passengerbooking',
            name='flight_class',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='passenger_bookings', to='flights.travelclass'),
        ),
        migrations.AddField(
            model_name='passengerbooking',
            name='passenger_type',
            field=models.CharField(choices=[('adult', 'Adult'), ('child', 'Child'), ('infant', 'Infant')], default='LEGACY-', max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='passengerbooking',
            name='seat_selection_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='passengerbooking',
            name='status',
            field=models.CharField(choices=[('booked', 'Booked'), ('checked_in', 'Checked In'), ('boarded', 'Boarded'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='booked', max_length=20),
        ),
        migrations.AlterField(
            model_name='passengerbooking',
            name='base_fare',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='passengerbooking',
            name='flight',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='passenger_bookings', to='flights.flight'),
        ),
        migrations.AlterField(
            model_name='passengerbooking',
            name='passenger',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='passenger_bookings', to='bookings.passenger'),
        ),
        migrations.AlterField(
            model_name='passengerbooking',
            name='seat_number',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='booked_by_agent_code',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='booked_by_user',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='booking_date',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='booking_reference',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='booking_status',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='booking_type',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='checked_baggage_count',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='checked_baggage_weight',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='checked_in_by',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='discount',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='fees',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='flight_sector',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='payment_status',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='seat_preference',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='special_requests',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='taxes',
        ),
        migrations.RemoveField(
            model_name='passengerbooking',
            name='total_amount',
        ),
    ]
