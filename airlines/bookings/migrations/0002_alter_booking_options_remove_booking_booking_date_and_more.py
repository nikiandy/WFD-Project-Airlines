

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'ordering': ['-created_at'], 'verbose_name': 'Booking', 'verbose_name_plural': 'Bookings'},
        ),
        migrations.RemoveField(
            model_name='booking',
            name='booking_date',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='booking_reference',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='in_flight_meal',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='lounge_access',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='passengers',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='priority_boarding',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='schedule',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='seat_class',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='total_price',
        ),
        migrations.RemoveField(
            model_name='passenger',
            name='special_assistance_details',
        ),
        migrations.AddField(
            model_name='booking',
            name='additional_services_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='base_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='contact_email',
            field=models.EmailField(default=False, max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='contact_phone',
            field=models.CharField(default='+0000000000', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='has_airport_pickup',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='booking',
            name='has_oversized_baggage',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='booking',
            name='has_premium_meal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='booking',
            name='has_priority_boarding',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='booking',
            name='has_sport_equipment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='booking',
            name='has_travel_insurance',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='booking',
            name='meal_preference',
            field=models.CharField(choices=[('standard', 'Standard'), ('vegetarian', 'Vegetarian'), ('vegan', 'Vegan'), ('gluten_free', 'Gluten Free'), ('kosher', 'Kosher'), ('halal', 'Halal'), ('diabetic', 'Diabetic'), ('low_sodium', 'Low Sodium')], default='standard', max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_status',
            field=models.CharField(choices=[('paid', 'Paid'), ('pending', 'Pending'), ('refunded', 'Refunded'), ('failed', 'Failed')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='booking',
            name='reference_number',
            field=models.CharField(default=0, max_length=10, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='tax_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='passenger',
            name='middle_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='passenger',
            name='special_requirements',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='extra_baggage',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='booking',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL),
        ),
    ]
