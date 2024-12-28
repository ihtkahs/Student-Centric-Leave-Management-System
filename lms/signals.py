from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Semester, Student

@receiver(post_save, sender=Semester)
def reset_leave_for_new_semester(sender, instance, **kwargs):
    if instance.is_active and not kwargs.get('raw', False):
        # Deactivate other semesters (without triggering signals)
        Semester.objects.filter(
            year=instance.year,
        ).exclude(id=instance.id).update(is_active=False)

        # Update student records without recursion
        active_semesters = Semester.objects.filter(is_active=True)

        for student in Student.objects.all():
            matching_semester = active_semesters.filter(
                year=student.year,
            ).first()

            # Update without triggering save()
            if matching_semester and student.current_semester != matching_semester:
                Student.objects.filter(id=student.id).update(
                    current_semester=matching_semester,
                    leave_taken=0,
                    balance_leave=6
                )
