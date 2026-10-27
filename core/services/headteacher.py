from core.models import Students, Classes, FeePayments, Terms, Users, FeeStructure, Marks, FeeWaivers, ReportCardApprovals, ReportCards, AuditLog
from django.db.models import Sum, Avg, Count
from decimal import Decimal

def get_headteacher_dashboard_data(term_id=None):
    # Fallback to current/latest term if none selected
    terms_dropdown = Terms.objects.all().order_by('-academic_year', '-term_name')
    active_term = Terms.objects.get(pk=term_id) if term_id else terms_dropdown.first()

    if not active_term:
        return {'terms': []}

    # 1. Standard Core Counters
    total_students = Students.objects.count()
    total_classes = Classes.objects.count()
    total_staff = Users.objects.count()

    # 2. Financial Metrics Calculations
    total_collected = FeePayments.objects.filter(term=active_term).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
    
    # Calculate expected tuition fees using enrollment counts multiplied by required class structures
    total_expected = Decimal('0.00')
    defaulters_count = 0
    structures = FeeStructure.objects.filter(term=active_term)
    
    for fs in structures:
        student_count_in_class = Students.objects.filter(class_field=fs.class_field).count()
        total_expected += (fs.amount_required * student_count_in_class)
        
        # Cross-reference students to check who owes balances
        class_students = Students.objects.filter(class_field=fs.class_field)
        for student in class_students:
            paid = FeePayments.objects.filter(student=student, term=active_term).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
            if paid < fs.amount_required:
                defaulters_count += 1

    # 3. Academic Analytics Systems
    term_marks = Marks.objects.filter(term=active_term)
    school_average = term_marks.aggregate(Avg('score'))['score__avg'] or Decimal('0.00')

    # Detect highest performing and lowest performing streams
    class_performances = term_marks.values('student__class_field__class_name').annotate(avg_score=Avg('score')).order_by('-avg_score')
    best_class = class_performances.first()['student__class_field__class_name'] if class_performances.exists() else "N/A"
    weakest_class = class_performances.last()['student__class_field__class_name'] if class_performances.exists() else "N/A"

    # 4. Global Alert Counters
    pending_approvals_count = ReportCards.objects.exclude(reportcardapprovals__status='APPROVED').count()
    pending_waivers_count = FeeWaivers.objects.filter(status='PENDING').count()

    return {
        'total_students': total_students,
        'total_classes': total_classes,
        'total_staff': total_staff,
        'total_collected': total_collected,
        'total_expected': total_expected,
        'defaulters_count': defaulters_count,
        'school_average': round(school_average, 2),
        'best_class': best_class,
        'weakest_class': weakest_class,
        'pending_approvals_count': pending_approvals_count,
        'pending_waivers_count': pending_waivers_count,
        'active_term': active_term,
        'terms': terms_dropdown
    }
