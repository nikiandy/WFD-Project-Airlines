

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlightClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=5)),
                ('description', models.TextField(blank=True)),
                ('price_factor', models.DecimalField(decimal_places=2, default=1.0, help_text='Multiplier applied to base fare (e.g., 1.0 for Economy, 2.5 for Business)', max_digits=4)),
                ('has_priority_boarding', models.BooleanField(default=False)),
                ('has_lounge_access', models.BooleanField(default=False)),
                ('has_premium_meals', models.BooleanField(default=False)),
                ('has_flat_bed', models.BooleanField(default=False)),
                ('checked_baggage_allowance', models.PositiveSmallIntegerField(default=1)),
                ('baggage_weight_allowance', models.PositiveSmallIntegerField(default=23)),
                ('carry_on_allowance', models.PositiveSmallIntegerField(default=1)),
                ('display_order', models.PositiveSmallIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Flight Class',
                'verbose_name_plural': 'Flight Classes',
                'ordering': ['display_order', 'price_factor'],
            },
        ),
    ]
