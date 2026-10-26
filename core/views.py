from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Users, Students, Classes

def login_view(request):
    """Handles core authentication using the custom MySQL users table."""
    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_hash = request.POST.get('password')
        
        try:
            user = Users.objects.get(username=u_name)
            if user.password_hash == p_hash or user.password_hash.strip() == p_hash.strip():
                if user.is_active == 0:
                    messages.error(request, "This staff account is currently deactivated.")
                    return render(request, 'core/login.html')
                
                request.session['user_id'] = user.user_id
                request.session['username'] = user.username
                request.session['user_role'] = user.role.upper()
                request.session['full_name'] = user.full_name
                
                role = user.role.upper()
                if role == 'HEADTEACHER': return redirect('headteacher_dashboard')
                elif role == 'TEACHER': return redirect('teacher_dashboard')
                elif role == 'DOS': return redirect('dos_dashboard')
                elif role == 'BURSAR': return redirect('bursar_dashboard')
                elif role == 'NURSE': return redirect('nurse_dashboard')
                else: return redirect('dashboard')
            else:
                messages.error(request, "Invalid password credentials provided.")
        except Users.DoesNotExist:
            messages.error(request, "No staff member found matching that username.")
            
    return render(request, 'core/login.html')

def logout_view(request):
    """Flushes active user sessions and routes to login."""
    request.session.flush()
    messages.info(request, "You have been logged out out of the system workspace safely.")
    return redirect('login')

def dashboard_view(request):
    """Generic fallback route based on authenticated staff roles."""
    role = request.session.get('user_role')
    if not role: return redirect('login')
    if role == 'HEADTEACHER': return redirect('headteacher_dashboard')
    elif role == 'TEACHER': return redirect('teacher_dashboard')
    elif role == 'DOS': return redirect('dos_dashboard')
    elif role == 'BURSAR': return redirect('bursar_dashboard')
    elif role == 'NURSE': return redirect('nurse_dashboard')
    return render(request, 'core/dashboard.html', {'title': 'General Panel'})

def student_list_view(request):
    students = Students.objects.all()
    return render(request, 'core/students.html', {'students': students, 'title': 'Student Directory Master'})

def add_student_view(request):
    classes = Classes.objects.all()
    return render(request, 'core/add_student.html', {'classes': classes, 'title': 'Enroll New Student'})

def marks_entry_view(request):
    return redirect('teacher_dashboard')

def fee_payments_view(request):
    return redirect('bursar_dashboard')
