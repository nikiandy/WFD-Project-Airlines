

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile_password_reset_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('planning_manager', 'Planning Manager'), ('staff', 'Staff'), ('customer', 'Customer')], default='customer', max_length=20),
        ),
    ]
