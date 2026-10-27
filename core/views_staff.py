from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from .models import Users, Students, Classes, Subjects, Terms, Marks, FeePayments, MedicalLogs, FeeStructure, ReportCards
from .permissions import school_role_required

# =========================================================================
# 🧑‍🏫 TEACHER WORKSPACE
# =========================================================================
@school_role_required(allowed_roles=['TEACHER', 'HEADTEACHER'])
def teacher_dashboard(request):
    """View to see managed classrooms and academic terms."""
    teacher_id = request.session.get('user_id')
    teacher = get_object_or_404(Users, pk=teacher_id)
    assigned_classes = Classes.objects.filter(class_teacher=teacher)
    all_terms = Terms.objects.all().order_by('-academic_year', '-term_name')
    
    context = {
        'title': 'Teacher Workspace',
        'teacher': teacher,
        'assigned_classes': assigned_classes,
        'terms': all_terms,
    }
    return render(request, 'core/teacher/dashboard.html', context)


@school_role_required(allowed_roles=['TEACHER'])
def enter_marks(request, class_id):
    """Form processing view to submit or update student exam records."""
    target_class = get_object_or_404(Classes, pk=class_id)
    students = Students.objects.filter(class_field=target_class)
    subjects = Subjects.objects.filter(class_field=target_class)
    terms = Terms.objects.all()
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        term_id = request.POST.get('term')
        max_score = Decimal(request.POST.get('max_score', '100.00'))
        
        subject_obj = get_object_or_404(Subjects, pk=subject_id)
        term_obj = get_object_or_404(Terms, pk=term_id)
        teacher_obj = get_object_or_404(Users, pk=request.session.get('user_id'))
        
        for student in students:
            score_val = request.POST.get(f'score_{student.student_id}')
            if score_val:
                Marks.objects.update_or_create(
                    student=student,
                    subject=subject_obj,
                    term=term_obj,
                    defaults={
                        'teacher': teacher_obj,
                        'score': Decimal(score_val),
                        'max_score': max_score,
                        'date_recorded': timezone.now()
                    }
                )
        messages.success(request, f"Academic marks saved successfully for {target_class.class_name}.")
        return redirect('teacher_dashboard')

    context = {
        'target_class': target_class,
        'students': students,
        'subjects': subjects,
        'terms': terms,
    }
    return render(request, 'core/teacher/enter_marks.html', context)


# =========================================================================
# 🎓 DIRECTOR OF STUDIES (DOS) WORKSPACE
# =========================================================================
@school_role_required(allowed_roles=['DOS', 'HEADTEACHER'])
def dos_dashboard(request):
    """Curriculum view panel handling bulk student report sheet compilation."""
    classes = Classes.objects.all()
    total_students = Students.objects.count()
    subjects = Subjects.objects.all()
    all_terms = Terms.objects.all()
    
    if request.method == 'POST' and request.POST.get('action') == 'compile_reports':
        target_term_id = request.POST.get('term_id')
        term_obj = get_object_or_404(Terms, pk=target_term_id)
        
        all_students = Students.objects.all()
        compiled_count = 0
        
        for student in all_students:
            student_marks = Marks.objects.filter(student=student, term=term_obj)
            if student_marks.exists():
                total = student_marks.aggregate(Sum('score'))['score__sum'] or Decimal('0.00')
                average = student_marks.aggregate(Avg('score'))['score__avg'] or Decimal('0.00')
                
                if average >= 80:
                    grade_letter, teacher_remarks = 'A', 'Excellent performance! Keeps practicing consistency.'
                elif average >= 65:
                    grade_letter, teacher_remarks = 'B', 'Very good progress made this term cycle.'
                elif average >= 50:
                    grade_letter, teacher_remarks = 'C', 'Fair performance, can strive for better grades.'
                else:
                    grade_letter, teacher_remarks = 'F', 'Needs intensive remedial supervision next session.'
                
                ReportCards.objects.update_or_create(
                    student=student,
                    term=term_obj,
                    defaults={
                        'total_score': total,
                        'average_score': average,
                        'grade': grade_letter,
                        'remarks': teacher_remarks,
                        'generated_date': timezone.now()
                    }
                )
                compiled_count += 1
                
        messages.success(request, f"Successfully processed terminal reports for {compiled_count} students!")
        return redirect('dos_dashboard')

    context = {
        'title': 'Director of Studies (DOS) Dashboard',
        'classes': classes,
        'total_students': total_students,
        'subjects': subjects,
        'terms': all_terms,
    }
    return render(request, 'core/dos/dashboard.html', context)


# =========================================================================
# 💰 BURSAR WORKSPACE
# =========================================================================
@school_role_required(allowed_roles=['BURSAR', 'HEADTEACHER'])
def bursar_dashboard(request):
    """Tuition records tracker logging student fee collection references."""
    recent_payments = FeePayments.objects.all().order_by('-payment_date')[:10]
    students = Students.objects.all()
    terms = Terms.objects.all()
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        term_id = request.POST.get('term')
        amount = Decimal(request.POST.get('amount_paid'))
        receipt = request.POST.get('receipt_no')
        bursar_obj = get_object_or_404(Users, pk=request.session.get('user_id'))
        
        FeePayments.objects.create(
            student=get_object_or_404(Students, pk=student_id),
            term=get_object_or_404(Terms, pk=term_id),
            amount_paid=amount,
            payment_date=timezone.now(),
            receipt_no=receipt,
            received_by=bursar_obj
        )
        messages.success(request, f"Payment recorded successfully! Receipt Reference: {receipt}")
        return redirect('bursar_dashboard')
        
    context = {
        'title': 'Bursar Financial Dashboard',
        'recent_payments': recent_payments,
        'students': students,
        'terms': terms,
    }
    return render(request, 'core/bursar/dashboard.html', context)


# =========================================================================
# 🩺 NURSE SICKBAY WORKSPACE
# =========================================================================
@school_role_required(allowed_roles=['NURSE', 'HEADTEACHER'])
def nurse_dashboard(request):
    """Admission logger recording treatments administered to students."""
    medical_records = MedicalLogs.objects.all().order_by('-visit_date')
    students = Students.objects.all()
    active_terms = Terms.objects.all()
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        term_id = request.POST.get('term')
        symptoms = request.POST.get('symptoms')
        treatment = request.POST.get('treatment_given')
        nurse_obj = get_object_or_404(Users, pk=request.session.get('user_id'))
        
        MedicalLogs.objects.create(
            student=get_object_or_404(Students, pk=student_id),
            term=get_object_or_404(Terms, pk=term_id),
            symptoms=symptoms,
            treatment_given=treatment,
            logged_by=nurse_obj
        )
        messages.success(request, "Medical incident card saved successfully in sickbay log.")
        return redirect('nurse_dashboard')

    context = {
        'title': 'Nurse Sickbay Station',
        'medical_records': medical_records,
        'students': students,
        'terms': active_terms,
    }
    return render(request, 'core/nurse/dashboard.html', context)
