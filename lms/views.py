from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from .forms import LeaveApplicationForm
from .models import Student, LeaveRequest, Counsellor
from django.core.mail import send_mail
from django.conf import settings

# Custom login view
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Check if the user is a staff or student
            if hasattr(user, 'counsellor'):  # If the user is linked to a counsellor record
                return redirect('counsellor_dashboard')
            elif hasattr(user, 'hod'):  # If the user is linked to an HOD record
                return redirect('hod_dashboard')
            elif hasattr(user, 'student'):  # If the user is linked to a student record
                return redirect('student_dashboard')
            else:
                return HttpResponse("Unauthorized access or role not assigned")
        else:
            return HttpResponse("Invalid credentials")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Dashboard Views
@login_required
def student_dashboard(request):
    # You can pass any context you need here
    return render(request, 'student_dashboard.html')

@login_required
def counsellor_dashboard(request):
    # You can pass any context you need here
    return render(request, 'counsellor_dashboard.html')

@login_required
def hod_dashboard(request):
    # You can pass any context you need here
    return render(request, 'hod_dashboard.html')

@login_required
def my_profile(request):
    # Fetch the logged-in student's profile
    student = Student.objects.get(user=request.user)  # Assuming user is logged in
    context = {'student': student}
    return render(request, 'my_profile.html', context)

@login_required
def apply_leave(request):
    if request.method == "POST":
        form = LeaveApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the logged-in student
            student = Student.objects.get(user=request.user)
            # Fetch the student's counsellor
            counsellor = student.counsellor

            # Save the leave request data
            LeaveRequest.objects.create(
                student=student,
                counsellor=counsellor,
                leave_type=form.cleaned_data["leave_type"],
                duration=form.cleaned_data["duration"],
                date=form.cleaned_data["date"],
                start_date=form.cleaned_data["start_date"],
                end_date=form.cleaned_data["end_date"],
                reason=form.cleaned_data["reason"],
                proof=form.cleaned_data["proof"],
            )

            # Send a success email
            subject="Leave Request Submitted Successfully"
            message=(
                        f"Dear {student.user.first_name},\n\nYour leave request has been submitted successfully. "
                        f"Here are the details:\n\n"
                        f"Leave Type: {form.cleaned_data['leave_type']}\n"
                        f"Duration: {form.cleaned_data['duration']}\n"
                        f"Reason: {form.cleaned_data['reason']}\n"
                        f"Date: {form.cleaned_data['date']}\n"
                        f"Start Date: {form.cleaned_data['start_date'] or 'N/A'}\n"
                        f"End Date: {form.cleaned_data['end_date'] or 'N/A'}\n\n"
                        f"Thank you,\nLeave Management System"
            )
            email = student.email
            recipient_list=[email]
            send_mail(subject, message, "ihtkahs251004@gmail.com", recipient_list, fail_silently=True)

            success_message = "Leave submitted successfully!"
            return render(request, "apply_leave.html", {"form": form, "success_message": success_message})
    else:
        form = LeaveApplicationForm()

    return render(request, "apply_leave.html", {"form": form})

def logout_view(request):
    logout(request)  # This will log out the user
    return redirect('homepage')

def homepage(request):
    return render(request, 'homepage.html')
