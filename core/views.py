from django.contrib import messages
from django.shortcuts import render, redirect

from .models import Users, Students, Classes
from .permissions import school_role_required
from .roles import role_code, HOME_PAGES


def login_view(request):
    """Checks the username and password against the users table."""
    if request.method == 'POST':
        u_name = (request.POST.get('username') or '').strip()
        p_value = (request.POST.get('password') or '').strip()

        try:
            user = Users.objects.get(username=u_name)
        except Users.DoesNotExist:
            messages.error(request, "No staff member found matching that username.")
            return render(request, 'core/login.html')

        if user.password_hash.strip() != p_value:
            messages.error(request, "Invalid password credentials provided.")
            return render(request, 'core/login.html')

        if user.is_active == 0:
            messages.error(request, "This staff account is currently deactivated.")
            return render(request, 'core/login.html')

        code = role_code(user.role)
        if code is None:
            messages.error(request, "This account has a role the system does not recognise. Contact the headteacher.")
            return render(request, 'core/login.html')

        request.session.flush()  # start from a clean session
        request.session['user_id'] = user.user_id
        request.session['username'] = user.username
        request.session['user_role'] = code
        request.session['full_name'] = user.full_name
        return redirect(HOME_PAGES.get(code, 'dashboard'))

    return render(request, 'core/login.html')


def logout_view(request):
    request.session.flush()
    messages.info(request, "You have been logged out safely.")
    return redirect('login')


def dashboard_view(request):
    """Sends each role to its own workspace."""
    code = request.session.get('user_role')
    if not code:
        return redirect('login')
    if code in HOME_PAGES:
        return redirect(HOME_PAGES[code])
    return render(request, 'core/dashboard.html', {'title': 'General Panel'})


@school_role_required(allowed_roles=['HEADTEACHER', 'DEPUTY', 'DOS', 'BURSAR', 'TEACHER'])
def student_list_view(request):
    students = Students.objects.select_related('class_field')
    if request.session.get('user_role') == 'TEACHER':
        # Teachers only see the class they are assigned to
        students = students.filter(class_field__class_teacher=request.session.get('user_id'))
    return render(request, 'core/students.html', {'students': students, 'title': 'Student Directory'})


@school_role_required(allowed_roles=['HEADTEACHER', 'DEPUTY'])
def add_student_view(request):
    classes = Classes.objects.all()
    return render(request, 'core/add_student.html', {'classes': classes, 'title': 'Enroll New Student'})


def marks_entry_view(request):
    return redirect('teacher_dashboard')


def fee_payments_view(request):
    return redirect('bursar_dashboard')