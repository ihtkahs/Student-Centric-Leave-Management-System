from django.contrib import admin
from .models import Student, Counsellor, HOD, LeaveRequest, LeaveStatus, Semester
from django.db.models.signals import post_save
from django.dispatch import receiver

admin.site.register(Student)
admin.site.register(Counsellor)
admin.site.register(HOD)
admin.site.register(LeaveRequest)
admin.site.register(LeaveStatus)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'start_date', 'end_date', 'is_active')
    list_filter = ('year', 'is_active')
    actions = ['activate_semester']

    def activate_semester(self, request, queryset):
        for semester in queryset:
            semester.is_active = True
            semester.save()
        self.message_user(request, "Selected semesters activated.")

@receiver(post_save, sender=Student)
def assign_semester_on_student_creation(sender, instance, **kwargs):
    active_semester = Semester.objects.filter(
        year=instance.year,
        is_active=True
    ).first()

    if active_semester:
        instance.current_semester = active_semester
        instance.save()
