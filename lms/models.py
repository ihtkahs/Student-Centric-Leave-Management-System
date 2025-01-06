from django.db import models
from django.contrib.auth.models import User

class Semester(models.Model):
    SEMESTER_CHOICES = [
        (1, "Semester 1"),
        (2, "Semester 2"),
        (3, "Semester 3"),
        (4, "Semester 4"),
        (5, "Semester 5"),
        (6, "Semester 6"),
    ]

    name = models.IntegerField(choices=SEMESTER_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    year = models.IntegerField()  # Year of study (1st, 2nd, etc.)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_active:
            Semester.objects.filter(
                year=self.year,
            ).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)  # Avoid calling save() again

    def __str__(self):
        return f"{self.get_name_display()} - {self.year} Year"

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
    counsellor = models.ForeignKey("Counsellor", on_delete=models.SET_NULL, null=True, blank=True)
    current_semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - Year {self.year} - {self.department}"

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
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    counsellor = models.ForeignKey(Counsellor, on_delete=models.SET_NULL, null=True, blank=True)
    leave_type = models.CharField(max_length=20)
    duration = models.CharField(max_length=10)
    date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    reason = models.TextField()
    proof = models.FileField(upload_to='proofs/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.leave_type}"

class LeaveStatus(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved_by_counsellor', 'Approved by Counsellor'),
        ('rejected_by_counsellor', 'Rejected by Counsellor'),
        ('approved_by_hod', 'Approved by HOD'),
        ('rejected_by_hod', 'Rejected by HOD'),
        ('final_approved', 'Final Approved'),
        ('final_rejected', 'Final Rejected'),
    ]

    leave_request = models.ForeignKey(LeaveRequest, related_name="status_history", on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, default=1)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    counsellor_comment = models.TextField(null=True, blank=True)
    hod_comment = models.TextField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Status for LeaveRequest {self.leave_request.id} - {self.status} - {self.student.id}"
