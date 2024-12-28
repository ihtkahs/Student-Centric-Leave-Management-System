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
from datetime import timedelta

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
    semester = student.current_semester
    context = {'student': student, 'semester': semester,}
    return render(request, 'my_profile.html', context)

@login_required
def apply_leave(request):
    if request.method == "POST":
        form = LeaveApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the logged-in student
            student = Student.objects.get(user=request.user)
            print(student)
            # Fetch the student's counsellor
            counsellor = student.counsellor
            print(counsellor)

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

    counsellor = request.user.counsellor
    leave_requests = LeaveRequest.objects.filter(
        status_history__status='pending',
        student__counsellor=counsellor
    ).select_related('student').distinct()

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')

        leave_request = get_object_or_404(LeaveRequest, id=leave_id)
        leave_status = leave_request.status_history.last()

        if leave_request.student.counsellor != counsellor:
            messages.error(request, "Unauthorized action!")
            return redirect('counsellor_dashboard')

        student_email = leave_request.student.email  # Get the student's email
        student_name = leave_request.student.name  # Get the student's name

        # Update leave status based on action
        if action == 'approve':
            leave_status.status = 'approved_by_counsellor'
            leave_status.counsellor_comment = comments
            leave_status.save()

            # Notify the student about the approval and forward to HOD
            subject = "Your Leave Request Has Been Approved by the Counsellor"
            message = (
                f"Dear {student_name},\n\n"
                f"Your leave request for {leave_request.leave_type} has been approved by your counsellor.\n\n"
                f"Reason: {leave_request.reason}\n"
                f"Date: {leave_request.date}\n\n"
                f"Start Date: {leave_request.start_date}\n"
                f"End Date: {leave_request.end_date}\n\n"
                f"Comments from Counsellor: {comments}\n\n"
                f"Your leave request is now being forwarded to the HOD for further approval.\n\n"
                f"Best regards,\nLeave Management System"
            )
            send_mail(subject, message, "ihtkahs251004@gmail.com", [student_email], fail_silently=True)

            messages.success(request, "Leave request forwarded to HOD.")
        
        elif action == 'reject':
            leave_status.status = 'rejected_by_counsellor'
            leave_status.counsellor_comment = comments
            leave_status.save()

            # Notify the student about the rejection
            subject = "Your Leave Request Has Been Rejected by the Counsellor"
            message = (
                f"Dear {student_name},\n\n"
                f"Unfortunately, your leave request for {leave_request.leave_type} has been rejected by your counsellor.\n\n"
                f"Reason: {leave_request.reason}\n"
                f"Date: {leave_request.date}\n\n"
                f"Start Date: {leave_request.start_date}\n"
                f"End Date: {leave_request.end_date}\n\n"
                f"Comments from Counsellor: {comments}\n\n"
                f"Please contact your counsellor for more details.\n\n"
                f"Best regards,\nLeave Management System"
            )
            send_mail(subject, message, "ihtkahs251004@gmail.com", [student_email], fail_silently=True)

            messages.success(request, "Leave request rejected.")

        return redirect('counsellor_approve_leave')

    return render(request, 'counsellor_approve_leave.html', {'leave_requests': leave_requests, 'user_role': request.user})
    

@login_required
def hod_approve_leave(request):
    if not hasattr(request.user, 'hod'):  # Ensure the user is an HOD
        return redirect('home')  # Redirect to the home page if not an HOD

    hod = request.user.hod

    # Filter leave requests that are approved by counsellor and pending HOD approval
    leave_requests = LeaveRequest.objects.filter(
        status_history__status='approved_by_counsellor',
        student__department=hod.department  # Filter leave requests for the HOD's department
    ).select_related('student').distinct()

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')

        leave_request = get_object_or_404(LeaveRequest, id=leave_id)
        leave_status = leave_request.status_history.last()

        # Ensure the HOD is handling leave requests for their department
        if leave_request.student.department != hod.department:
            messages.error(request, "Unauthorized action!")
            return redirect('hod_dashboard')

        student = leave_request.student
        student_email = leave_request.student.email
        student_name = leave_request.student.name

        # Calculate leave days
        def calculate_leave_days(start, end):
            leave_days = 0
            current_date = start
            while current_date <= end:
                # Exclude Sundays (weekday 6 is Sunday)
                if current_date.weekday() != 6:
                    leave_days += 1
                current_date += timedelta(days=1)
            return leave_days

        # Update leave status based on action
        if action == 'approve':
            leave_status.status = 'approved_by_hod'
            leave_status.hod_comment = comments
            leave_status.save()

            # Calculate leave days and update student record
            if leave_request.duration == 'single':
                leave_days = 1
            else:
                leave_days = calculate_leave_days(
                    leave_request.start_date,
                    leave_request.end_date
                )

            student.leave_taken += leave_days
            student.balance_leave -= leave_days
            student.save()

            # Notify student about the HOD's approval
            subject = "Your Leave Request Has Been Approved by the HOD"
            message = (
                f"Dear {student_name},\n\n"
                f"Your leave request for {leave_request.leave_type} has been approved by the HOD.\n\n"
                f"Details:\n"
                f"Reason: {leave_request.reason}\n"
                f"Date: {leave_request.date}\n"
                f"Start Date: {leave_request.start_date}\n"
                f"End Date: {leave_request.end_date}\n\n"
                f"Comments from HOD: {comments}\n\n"
                f"Enjoy your leave!\n\n"
                f"Best regards,\nLeave Management System"
            )
            send_mail(subject, message, "ihtkahs251004@gmail.com", [student_email], fail_silently=True)

            messages.success(request, "Leave request approved successfully.")

        elif action == 'reject':
            leave_status.status = 'rejected_by_hod'
            leave_status.hod_comment = comments
            leave_status.save()

            # Notify student about the HOD's rejection
            subject = "Your Leave Request Has Been Rejected by the HOD"
            message = (
                f"Dear {student_name},\n\n"
                f"Unfortunately, your leave request for {leave_request.leave_type} has been rejected by the HOD.\n\n"
                f"Details:\n"
                f"Reason: {leave_request.reason}\n"
                f"Date: {leave_request.date}\n"
                f"Start Date: {leave_request.start_date}\n"
                f"End Date: {leave_request.end_date}\n\n"
                f"Comments from HOD: {comments}\n\n"
                f"Please contact the HOD for further clarification.\n\n"
                f"Best regards,\nLeave Management System"
            )
            send_mail(subject, message, "ihtkahs251004@gmail.com", [student_email], fail_silently=True)

            messages.success(request, "Leave request rejected.")

        return redirect('hod_approve_leave')

    return render(request, 'hod_approve_leave.html', {'leave_requests': leave_requests, 'user_role': request.user})

@login_required
def leave_history(request):
    # You can pass any context you need here
    return render(request, 'leave_history.html')

def logout_view(request):
    logout(request)  # This will log out the user
    return redirect('homepage')

def homepage(request):
    return render(request, 'homepage.html')
