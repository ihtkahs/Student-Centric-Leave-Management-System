# Generated by Django 3.2.20 on 2024-12-14 10:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0007_leaverequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='counsellor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lms.counsellor'),
        ),
    ]
