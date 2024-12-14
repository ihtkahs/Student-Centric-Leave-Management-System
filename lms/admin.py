from django.contrib import admin
from .models import Student, Counsellor, HOD, LeaveRequest

admin.site.register(Student)
admin.site.register(Counsellor)
admin.site.register(HOD)
admin.site.register(LeaveRequest)
