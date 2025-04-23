

import django.core.validators
from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaggageAllowance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cabin_baggage_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('cabin_baggage_weight', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('checked_baggage_count', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('checked_baggage_weight', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('extra_baggage_fee_paid', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('has_sports_equipment', models.BooleanField(default=False)),
                ('sports_equipment_description', models.CharField(blank=True, max_length=255)),
                ('sports_equipment_fee_paid', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('has_musical_instrument', models.BooleanField(default=False)),
                ('musical_instrument_description', models.CharField(blank=True, max_length=255)),
                ('musical_instrument_fee_paid', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Baggage Allowance',
                'verbose_name_plural': 'Baggage Allowances',
            },
        ),
        migrations.CreateModel(
            name='BaggageItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('baggage_type', models.CharField(choices=[('cabin', 'Cabin Baggage'), ('checked', 'Checked Baggage'), ('sports', 'Sports Equipment'), ('musical', 'Musical Instrument'), ('other', 'Other Special Item')], max_length=20)),
                ('description', models.CharField(max_length=255)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)])),
                ('dimensions', models.CharField(help_text='Format: LxWxH in cm', max_length=50)),
                ('color', models.CharField(blank=True, max_length=50)),
                ('tag_number', models.CharField(max_length=20, unique=True)),
                ('barcode', models.CharField(blank=True, max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending Check-in'), ('checked_in', 'Checked In'), ('in_transit', 'In Transit'), ('arrived', 'Arrived at Destination'), ('claimed', 'Claimed by Passenger'), ('lost', 'Lost'), ('damaged', 'Damaged')], default='pending', max_length=20)),
                ('checked_in_at', models.DateTimeField(blank=True, null=True)),
                ('checked_in_location', models.CharField(blank=True, max_length=100)),
                ('claimed_at', models.DateTimeField(blank=True, null=True)),
                ('claiming_location', models.CharField(blank=True, max_length=100)),
                ('requires_special_handling', models.BooleanField(default=False)),
                ('special_handling_instructions', models.TextField(blank=True)),
                ('contains_fragile_items', models.BooleanField(default=False)),
                ('contains_dangerous_goods', models.BooleanField(default=False)),
                ('is_insured', models.BooleanField(default=False)),
                ('declared_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('has_issues', models.BooleanField(default=False)),
                ('issue_description', models.TextField(blank=True)),
                ('issue_reported_at', models.DateTimeField(blank=True, null=True)),
                ('issue_resolved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Baggage Item',
                'verbose_name_plural': 'Baggage Items',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BaggagePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('cabin_baggage_allowed', models.BooleanField(default=True)),
                ('cabin_baggage_max_count', models.PositiveSmallIntegerField(default=1)),
                ('cabin_baggage_max_weight', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)])),
                ('cabin_baggage_max_dimensions', models.CharField(help_text='Format: LxWxH in cm', max_length=50)),
                ('checked_baggage_allowed', models.BooleanField(default=True)),
                ('checked_baggage_max_count', models.PositiveSmallIntegerField(default=1)),
                ('checked_baggage_max_weight', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)])),
                ('checked_baggage_max_dimensions', models.CharField(help_text='Format: LxWxH in cm', max_length=50)),
                ('sports_equipment_allowed', models.BooleanField(default=False)),
                ('sports_equipment_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('musical_instruments_allowed', models.BooleanField(default=False)),
                ('musical_instruments_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('excess_weight_fee_per_kg', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)])),
                ('additional_bag_fee', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)])),
                ('prohibited_items', models.TextField(help_text='Comma-separated list of prohibited items')),
                ('is_active', models.BooleanField(default=True)),
                ('valid_from', models.DateField()),
                ('valid_until', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Baggage Policy',
                'verbose_name_plural': 'Baggage Policies',
            },
        ),
        migrations.CreateModel(
            name='BaggageTransfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_date', models.DateTimeField()),
                ('transfer_location', models.CharField(max_length=100)),
                ('transfer_status', models.CharField(choices=[('scheduled', 'Scheduled'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed')], default='scheduled', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('scheduled_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Baggage Transfer',
                'verbose_name_plural': 'Baggage Transfers',
                'ordering': ['transfer_date'],
            },
        ),
    ]
