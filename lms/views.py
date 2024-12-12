from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm

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

def logout_view(request):
    logout(request)  # This will log out the user
    return redirect('homepage')

def homepage(request):
    return render(request, 'homepage.html')
