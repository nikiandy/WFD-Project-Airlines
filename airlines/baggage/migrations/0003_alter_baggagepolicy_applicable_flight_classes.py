

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('baggage', '0002_initial'),
        ('flights', '0002_flightclass'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baggagepolicy',
            name='applicable_flight_classes',
            field=models.ManyToManyField(blank=True, related_name='baggage_policies', to='flights.flightclass'),
        ),
    ]
