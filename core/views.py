from django.shortcuts import render, redirect
from django.db import connection
from .models import Users

def login_view(request):
    if request.session.get('user_id'):
        return redirect('/dashboard/')
    error = None
    if request.method == 'POST':
        user_input = request.POST.get('username', '').strip().lower()
        pass_input = request.POST.get('password', '')
        try:
            user = Users.objects.get(username=user_input)
            if user.password_hash == pass_input:
                request.session['user_id'] = user.user_id
                request.session['full_name'] = user.full_name
                request.session['role'] = user.role
                return redirect('/dashboard/')
            else:
                error = "Invalid password entered."
        except Users.DoesNotExist:
            error = f"Username '{user_input}' does not exist."
    return render(request, 'core/login.html', {'error': error})

def logout_view(request):
    request.session.flush()
    return redirect('/login/')

def dashboard_view(request):
    if not request.session.get('user_id'):
        return redirect('/login/')
        
    role = request.session.get('role')
    user_id = request.session.get('user_id')
    stats = {}
    teacher_class = None
    
    with connection.cursor() as cursor:
        # Global metrics for general staff oversight
        cursor.execute("SELECT COUNT(*) FROM students")
        stats['total_students'] = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM classes")
        stats['total_classes'] = cursor.fetchone()

        # Custom logic for Class Teachers
        if role == 'teacher':
            # Identify which class stream this specific user manages based on subjects or marks history
            cursor.execute("""
                SELECT c.class_id, c.class_name 
                FROM classes c
                JOIN subjects s ON s.class_id = c.class_id
                WHERE s.teacher_id = %s LIMIT 1
            """, [user_id])
            row = cursor.fetchone()
            if row:
                teacher_class = {'id': row[0], 'name': row[1]}
                
                # Fetch student enrollment count specific only to this teacher's class stream
                cursor.execute("SELECT COUNT(*) FROM students WHERE class_id = %s", [row[0]])
                stats['my_class_students'] = cursor.fetchone()

        if role in ['bursar', 'admin']:
            cursor.execute("SELECT SUM(amount_paid) FROM fee_payments")
            stats['total_collected'] = cursor.fetchone() or 0
        
        if role in ['director_of_studies', 'teacher', 'admin']:
            cursor.execute("SELECT COUNT(*) FROM marks")
            stats['total_marks_recorded'] = cursor.fetchone()
            
    return render(request, 'core/dashboard.html', {
        'stats': stats, 
        'teacher_class': teacher_class
    })


def student_list_view(request):
    if not request.session.get('user_id'):
        return redirect('/login/')
        
    students_data = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.admission_no, s.full_name, s.gender, c.class_name 
            FROM students s 
            JOIN classes c ON c.class_id = s.class_id
            ORDER BY c.class_name, s.full_name
        """)
        # Stable column list mapping transformation
        columns = [col[0] for col in cursor.description]
        students_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    return render(request, 'core/students.html', {'students': students_data})

def add_student_view(request):
    if not request.session.get('user_id'):
        return redirect('/login/')
        
    classes_list = []
    error = None
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT class_id, class_name FROM classes ORDER BY class_name")
        classes_list = cursor.fetchall()
        
    if request.method == 'POST':
        adm_no = request.POST.get('admission_no', '').strip()
        name = request.POST.get('full_name', '').strip()
        gender = request.POST.get('gender', '')
        cls_id = request.POST.get('class_id', '')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO students (admission_no, full_name, gender, class_id) 
                    VALUES (%s, %s, %s, %s)
                """, [adm_no, name, gender, cls_id])
            return redirect('/students/')
        except Exception as e:
            error = f"Database Rejected Entry: {str(e)}"
            
    return render(request, 'core/add_student.html', {'classes': classes_list, 'error': error})
def marks_entry_view(request):
    if not request.session.get('user_id'):
        return redirect('/login/')
        
    error, success = None, None
    students, subjects, terms = [], [], []
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT student_id, full_name FROM students ORDER BY full_name")
        students = cursor.fetchall()
        cursor.execute("SELECT subject_id, subject_name FROM subjects ORDER BY subject_name")
        subjects = cursor.fetchall()
        cursor.execute("SELECT term_id, CONCAT(term_name, ' (', academic_year, ')') FROM terms")
        terms = cursor.fetchall()

    if request.method == 'POST':
        st_id = request.POST.get('student_id')
        sb_id = request.POST.get('subject_id')
        t_id = request.POST.get('term_id')
        score = request.POST.get('score')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO marks (student_id, subject_id, term_id, teacher_id, score, max_score) 
                    VALUES (%s, %s, %s, %s, %s, 100)
                """, [st_id, sb_id, t_id, request.session['user_id'], score])
            success = "Academic mark recorded successfully in the system ledger!"
        except Exception as e:
            error = f"Database Rejected Score: {str(e)}"
            
    return render(request, 'core/marks.html', {
        'students': students, 'subjects': subjects, 'terms': terms, 'error': error, 'success': success
    })

def fee_payments_view(request):
    if not request.session.get('user_id'):
        return redirect('/login/')
        
    error, success = None, None
    students, terms, history = [], [], []
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT student_id, full_name FROM students ORDER BY full_name")
        students = cursor.fetchall()
        cursor.execute("SELECT term_id, CONCAT(term_name, ' (', academic_year, ')') FROM terms")
        terms = cursor.fetchall()
        cursor.execute("""
            SELECT fp.receipt_no, s.full_name, fp.amount_paid, fp.payment_date 
            FROM fee_payments fp 
            JOIN students s ON s.student_id = fp.student_id 
            ORDER BY fp.payment_date DESC LIMIT 5
        """)
        history = cursor.fetchall()

    if request.method == 'POST':
        st_id = request.POST.get('student_id')
        t_id = request.POST.get('term_id')
        amount = request.POST.get('amount')
        rcpt = request.POST.get('receipt_no').strip()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO fee_payments (student_id, term_id, amount_paid, receipt_no, received_by) 
                    VALUES (%s, %s, %s, %s, %s)
                """, [st_id, t_id, amount, rcpt, request.session['user_id']])
            success = f"Payment of UGX {int(amount):,} processed. Receipt {rcpt} logged!"
            # Refresh history list
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT fp.receipt_no, s.full_name, fp.amount_paid, fp.payment_date 
                    FROM fee_payments fp JOIN students s ON s.student_id = fp.student_id 
                    ORDER BY fp.payment_date DESC LIMIT 5
                """)
                history = cursor.fetchall()
        except Exception as e:
            error = f"Transaction Terminated: {str(e)}"
            
    return render(request, 'core/fees.html', {
        'students': students, 'terms': terms, 'history': history, 'error': error, 'success': success
    })
