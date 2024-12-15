from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from .forms import LeaveApplicationForm
from .models import Student, LeaveRequest, Counsellor, LeaveStatus
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

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
            leave_request = LeaveRequest.objects.create(
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

            # Save the initial leave status
            LeaveStatus.objects.create(
                leave_request=leave_request,
                status='pending',
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

@login_required
def counsellor_approve_leave(request):
    if not hasattr(request.user, 'counsellor'):  # Ensure the user is a counsellor
        return redirect('home')  # Redirect to the home page if not a counsellor

    # Filter leave requests for the students assigned to this counsellor
    counsellor = request.user.counsellor
    leave_requests = LeaveRequest.objects.filter(
        status_history__status='pending',  # Use the reverse relation to filter by LeaveStatus
        student__counsellor=counsellor               # Ensure the leave request belongs to this counsellor's student
    ).select_related('student').distinct()

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')

        leave_request = get_object_or_404(LeaveRequest, id=leave_id)
        leave_status = leave_request.status_history.last()  # Get the latest status record

        # Ensure the counsellor is handling their student's leave request
        if leave_request.student.counsellor != counsellor:
            messages.error(request, "Unauthorized action!")
            return redirect('counsellor_dashboard')

        # Update leave status based on action
        if action == 'approve':
            leave_status.status = 'approved_by_counsellor'
            leave_status.counsellor_comment = comments
            leave_status.save()

            # Notify HOD only if counsellor approves
            messages.success(request, "Leave request forwarded to HOD.")
        elif action == 'reject':
            leave_status.status = 'rejected_by_counsellor'
            leave_status.counsellor_comment = comments
            leave_status.save()

            # Update leave request status as rejected
            messages.success(request, "Leave request rejected.")

        return redirect('counsellor_dashboard')

    return render(request, 'counsellor_approve_leave.html', {'leave_requests': leave_requests})

def logout_view(request):
    logout(request)  # This will log out the user
    return redirect('homepage')

def homepage(request):
    return render(request, 'homepage.html')
