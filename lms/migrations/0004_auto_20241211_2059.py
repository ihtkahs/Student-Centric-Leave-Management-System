# Generated by Django 3.2.20 on 2024-12-11 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0003_auto_20241211_2034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hod',
            name='user',
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='student',
        ),
        migrations.RemoveField(
            model_name='student',
            name='user',
        ),
        migrations.DeleteModel(
            name='Counsellor',
        ),
        migrations.DeleteModel(
            name='HOD',
        ),
        migrations.DeleteModel(
            name='LeaveRequest',
        ),
        migrations.DeleteModel(
            name='Student',
        ),
    ]
