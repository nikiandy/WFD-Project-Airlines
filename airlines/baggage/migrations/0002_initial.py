

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('baggage', '0001_initial'),
        ('bookings', '0001_initial'),
        ('flights', '0001_initial'),
        ('passengers', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='baggageallowance',
            name='booking',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='baggage_allowance', to='bookings.booking'),
        ),
        migrations.AddField(
            model_name='baggageallowance',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_baggage_allowances', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baggageitem',
            name='booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='baggage_items', to='bookings.booking'),
        ),
        migrations.AddField(
            model_name='baggageitem',
            name='checked_in_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checked_in_baggage', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baggageitem',
            name='passenger',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='baggage_items', to='passengers.passenger'),
        ),
        migrations.AddField(
            model_name='baggagepolicy',
            name='applicable_flight_classes',
            field=models.ManyToManyField(blank=True, related_name='baggage_policies', to='flights.travelclass'),
        ),
        migrations.AddField(
            model_name='baggagepolicy',
            name='applicable_flights',
            field=models.ManyToManyField(blank=True, related_name='baggage_policies', to='flights.flight'),
        ),
        migrations.AddField(
            model_name='baggageallowance',
            name='policy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='allowances', to='baggage.baggagepolicy'),
        ),
        migrations.AddField(
            model_name='baggagetransfer',
            name='baggage_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers', to='baggage.baggageitem'),
        ),
        migrations.AddField(
            model_name='baggagetransfer',
            name='destination_flight',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='baggage_transfers_to', to='flights.flight'),
        ),
        migrations.AddField(
            model_name='baggagetransfer',
            name='handled_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='handled_baggage_transfers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baggagetransfer',
            name='origin_flight',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='baggage_transfers_from', to='flights.flight'),
        ),
    ]
