# Generated by Django 5.1.6 on 2025-04-08 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0014_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaverequest',
            name='generated_pdf',
            field=models.FileField(blank=True, null=True, upload_to='leave_forms/'),
        ),
    ]
