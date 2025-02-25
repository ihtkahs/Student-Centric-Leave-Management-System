from django.db import models
from django.contrib.auth.models import User
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import re
from datetime import datetime
from django.core.mail import send_mail


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
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_name_display()} - {self.year} Year"


class Student(models.Model):
    reg_no = models.CharField(max_length=12, unique=True, null=True, blank=True, default=None)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
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
    staffID = models.CharField(max_length=12, unique=True, null=True, blank=True, default=None)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    name = models.CharField(max_length=100)
    year = models.IntegerField(blank=True, null=True)
    department = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class HOD(models.Model):
    staffID = models.CharField(max_length=12, unique=True, null=True, blank=True, default=None)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    counsellor = models.ForeignKey(Counsellor, on_delete=models.SET_NULL, null=True, blank=True)
    hod = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Added HOD reference
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, default=1)
    leave_type = models.CharField(max_length=20)
    duration = models.CharField(max_length=20)  # Changed from CharField to IntegerField
    date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    reason = models.TextField()
    proof = models.FileField(upload_to='proofs/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)  # Allow cancellation

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
    approved_at = models.DateTimeField(null=True, blank=True)  # Added timestamp for approval

    def save(self, *args, **kwargs):
        if self.status == 'final_approved':
            leave_days = self.leave_request.duration
            self.student.balance_leave -= leave_days
            self.student.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Status for LeaveRequest {self.leave_request.id} - {self.status} - {self.student.id}"


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    event_type = models.CharField(max_length=100, choices=[
        ('exam', 'Exam'),
        ('holiday', 'Holiday'),
        ('meeting', 'Meeting'),
    ])
    semester = models.ForeignKey('Semester', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class LeaveChatbot:
    def __init__(self):
        self.leave_request = {
            'leave_type': None,
            'duration': None,
            'reason': None,
            'date': None
        }
        self.state = {}  # To manage user state (progress through leave application)

    def get_response(self, user_message, student_email):
        message = user_message.lower()

        # Initialize state for new user
        if student_email not in self.state:
            self.state[student_email] = {'step': 1}

        current_step = self.state[student_email]['step']

        # Step 1: Ask for Leave Type
        if current_step == 1:
            if "apply leave" in message or "single day" in message:
                return "Got it! I can help you apply for leave. First, can you tell me what type of leave you want to apply for? (e.g., sick, casual, medical, personal)"

            if "casual" in message or "medical" in message or "personal" in message:
                self.leave_request['leave_type'] = message
                self.state[student_email]['step'] = 2
                return f"Got it! You want to apply for {self.leave_request['leave_type']} leave. Now, can you specify the duration of your leave (e.g., 1 day or 2 days)?"

        # Step 2: Ask for Duration
        elif current_step == 2:
            if re.search(r"\d+ day", message):
                # Check if leave duration is more than 2 days
                days = int(re.search(r"\d+", message).group())
                if days > 2:
                    return "Sorry, I can't process leave requests for more than 2 days. You can submit a leave request manually for that."
                self.leave_request['duration'] = message
                self.state[student_email]['step'] = 3
                return "Got it! Now, please provide a reason for your leave."

        # Step 3: Ask for Reason
        elif current_step == 3:
            if len(message.split()) == 1 and message in ['fever', 'headache', 'cold', 'family', 'emergency', 'hometown']:  # Short reasons
                self.leave_request['reason'] = message
                self.state[student_email]['step'] = 4
                return f"Thank you! You're requesting {self.leave_request['leave_type']} leave for {self.leave_request['duration']} due to '{self.leave_request['reason']}'. What date will you need the leave for?"

            if "reason" in message or len(message.split()) > 1:
                self.leave_request['reason'] = message
                self.state[student_email]['step'] = 4
                return f"Thank you for the details! You're requesting {self.leave_request['leave_type']} leave for {self.leave_request['duration']} due to '{self.leave_request['reason']}'. What date will you need the leave for?"

        # Step 4: Ask for Date
        elif current_step == 4:
            # Recognize and confirm the date format (DD-MM-YYYY)
            date_match = re.search(r"\b(\d{2})-(\d{2})-(\d{4})\b", message)
            if date_match:
                try:
                    self.leave_request['date'] = datetime.strptime(date_match.group(), "%d-%m-%Y").date()
                    self.state[student_email]['step'] = 5
                    return f"Your leave for {self.leave_request['date']} has been noted. Is everything correct? (yes/no)"
                except ValueError:
                    return "Sorry, I couldn't understand the date. Could you provide it in the format DD-MM-YYYY?"

        # Step 5: Confirm Details and Submit
        elif current_step == 5:
            if message.lower() == 'yes':
                # Submit leave request and send email
                self.submit_leave_request(student_email)
                self.state[student_email]['step'] = 1  # Reset the step for a new request
                return f"Leave form submitted successfully:\n" \
                       f"Leave Type: {self.leave_request['leave_type']}\n" \
                       f"Duration: {self.leave_request['duration']}\n" \
                       f"Reason: {self.leave_request['reason']}\n" \
                       f"Date: {self.leave_request['date']}\n" \
                       "A confirmation email has been sent to your email address."

            elif message.lower() == 'no':
                self.state[student_email]['step'] = 1  # Reset the step if they want to restart
                return "Let's start over. Please tell me the leave type again."

        # Default response for anything else
        return "Sorry, I didn't quite catch that. Can you tell me more about your leave request?"

    def submit_leave_request(self, student_email):
        # Here, you would handle creating the leave request and sending an email
        student = Student.objects.get(email=student_email)
        leave_type = self.leave_request['leave_type']
        duration = self.leave_request['duration']
        reason = self.leave_request['reason']
        leave_date = self.leave_request['date']

        # Create leave request object (use your models and logic as needed)
        leave_request = LeaveRequest.objects.create(
            student=student,
            leave_type=leave_type,
            duration=duration,
            reason=reason,
            date=leave_date
        )

        # Send confirmation email (use your send_email method)
        subject = "Leave Request Submitted"
        message = f"Your leave request has been submitted with the following details:\n" \
                  f"Leave Type: {leave_type}\nDuration: {duration}\nReason: {reason}\nDate: {leave_date}"
        send_mail(subject, message, "shakthi251004@gmail.com", [student.email], fail_silently=True)

def get_response(self, user_input):
    return self.chatbot.get_response(user_input)
