from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='password_reset_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ] 