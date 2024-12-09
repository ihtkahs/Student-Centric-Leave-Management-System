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

class Staff(models.Model):
    staffID = models.CharField(max_length=12, unique=True, null=True, blank=True, default=None)  # Staff ID for login
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)  # Link to Django User model
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=[('Counsellor', 'Counsellor'), ('HOD', 'HOD'), ('Year Incharge', 'Year Incharge')])
    year = models.IntegerField(blank=True, null=True)
    department = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} ({self.role})"

class LeaveRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=[('Casual', 'Casual'), ('Medical', 'Medical'), ('Privilege', 'Privilege')])
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    proof = models.FileField(upload_to='proofs/', blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending')
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"LeaveRequest: {self.student.name} ({self.leave_type})"
