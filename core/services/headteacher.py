from core.models import Students, Classes, FeePayments, Terms, Users

def get_headteacher_dashboard_data(term_id=None):
    """
    Safely calculates management data for the Headteacher command console.
    """
    # 1. Gather global data metrics
    try:
        student_count = Students.objects.count()
    except Exception:
        student_count = 0

    try:
        class_count = Classes.objects.count()
    except Exception:
        class_count = 0

    try:
        staff_count = Users.objects.count()
    except Exception:
        staff_count = 0

    # 2. Extract selected academic cycle criteria
    terms_dropdown = Terms.objects.all().order_by('-academic_year', '-term_name')
    active_term = None
    recent_transactions = []

    if term_id:
        try:
            active_term = Terms.objects.get(pk=term_id)
            recent_transactions = FeePayments.objects.filter(term=active_term).order_by('-payment_date')[:5]
        except Terms.DoesNotExist:
            pass
    
    # Fallback to the latest term if none is selected
    if not active_term and terms_dropdown.exists():
        active_term = terms_dropdown[0]
        try:
            recent_transactions = FeePayments.objects.filter(term=active_term).order_by('-payment_date')[:5]
        except Exception:
            recent_transactions = []

    # 3. Compile output dictionary matrix
    return {
        'total_students': student_count,
        'total_classes': class_count,
        'total_staff': staff_count,
        'terms': terms_dropdown,
        'active_term': active_term,
        'recent_transactions': recent_transactions,
    }
