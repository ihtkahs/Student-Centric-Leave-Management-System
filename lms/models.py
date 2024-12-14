from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    reg_no = models.CharField(max_length=12, unique=True, null=True, blank=True, default=None)  # Registration Number
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)  # Link to Django User model
    name = models.CharField(max_length=100)
    dob = models.DateField()
    year = models.IntegerField()
    department = models.CharField(max_length=50)
    section = models.CharField(max_length=5)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=10)
    leave_taken = models.IntegerField(default=0)
    balance_leave = models.IntegerField(default=6)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    def __str__(self):
        return self.name

class Counsellor(models.Model):
    staffID = models.CharField(max_length=12, unique=True, null=True, blank=True, default=None)  # Staff ID for login
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)  # Link to Django User model
    name = models.CharField(max_length=100)
    year = models.IntegerField(blank=True, null=True)
    department = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class HOD(models.Model):
    staffID = models.CharField(max_length=12, unique=True, null=True, blank=True, default=None)  # Staff ID for login
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)  # Link to Django User model
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    counsellor = models.ForeignKey(Counsellor, on_delete=models.SET_NULL, null=True, blank=True)
    leave_type = models.CharField(max_length=20)
    duration = models.CharField(max_length=10)
    date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    reason = models.TextField()
    proof = models.FileField(upload_to='proofs/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.leave_type} - {self.status}"
