from django.contrib import admin
from .models import Student, Staff, LeaveRequest

admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(LeaveRequest)
