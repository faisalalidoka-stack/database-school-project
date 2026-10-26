from django.db import connection


def get_terms():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT term_id, term_name, academic_year
            FROM terms
            ORDER BY academic_year DESC, start_date DESC
        """)
        return [{'id': r[0], 'label': f'{r[1]} {r[2]}'} for r in cursor.fetchall()]


def pick_term(terms, requested):
    """Use the requested term if valid, otherwise the newest term that has a fee structure."""
    try:
        requested = int(requested)
    except (TypeError, ValueError):
        requested = None

    for t in terms:
        if t['id'] == requested:
            return t

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT t.term_id
            FROM terms t
            WHERE EXISTS (SELECT 1 FROM fee_structure fs WHERE fs.term_id = t.term_id)
            ORDER BY t.academic_year DESC, t.start_date DESC
            LIMIT 1
        """)
        row = cursor.fetchone()

    if row:
        for t in terms:
            if t['id'] == row[0]:
                return t
    return terms[0] if terms else None


def get_dashboard_data(requested_term=None):
    terms = get_terms()
    term = pick_term(terms, requested_term)

    data = {
        'terms': terms,
        'term': term,
        'total_students': 0,
        'total_classes': 0,
        'total_staff': 0,
        'fees': {'expected': 0, 'collected': 0, 'outstanding': 0,
                 'students_with_balance': 0, 'rate': 0},
        'fees_by_class': [],
        'academics': {'school_average': None, 'best_class': None, 'weakest_class': None},
        'class_performance': [],
    }

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM students")
        data['total_students'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM classes")
        data['total_classes'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        data['total_staff'] = cursor.fetchone()[0]

        if term is None:
            return data
        term_id = term['id']

        # One row per student: what they owe and what they have paid this term
        cursor.execute("""
            SELECT c.class_name,
                   fs.amount_required,
                   IFNULL((SELECT SUM(fp.amount_paid)
                           FROM fee_payments fp
                           WHERE fp.student_id = s.student_id
                             AND fp.term_id = fs.term_id), 0) AS paid
            FROM students s
            JOIN classes c ON c.class_id = s.class_id
            JOIN fee_structure fs ON fs.class_id = s.class_id AND fs.term_id = %s
            ORDER BY c.class_name
        """, [term_id])
        student_rows = cursor.fetchall()

        # Average per class from the saved report cards
        cursor.execute("""
            SELECT c.class_name, ROUND(AVG(rc.average_score), 1) AS avg_score
            FROM report_cards rc
            JOIN students s ON s.student_id = rc.student_id
            JOIN classes c ON c.class_id = s.class_id
            WHERE rc.term_id = %s
            GROUP BY c.class_id, c.class_name
            ORDER BY avg_score DESC
        """, [term_id])
        class_rows = cursor.fetchall()

        cursor.execute("SELECT ROUND(AVG(average_score), 1) FROM report_cards WHERE term_id = %s", [term_id])
        school_avg = cursor.fetchone()[0]

    # Fees: totals and per-class breakdown
    expected = collected = outstanding = with_balance = 0
    by_class = {}
    for class_name, required, paid in student_rows:
        required = int(required)
        paid = int(paid)
        balance = required - paid
        expected += required
        collected += paid
        if balance > 0:
            outstanding += balance
            with_balance += 1
        entry = by_class.setdefault(class_name, {'class_name': class_name, 'students': 0,
                                                  'expected': 0, 'collected': 0})
        entry['students'] += 1
        entry['expected'] += required
        entry['collected'] += paid

    for entry in by_class.values():
        entry['balance'] = entry['expected'] - entry['collected']
        entry['rate'] = round(entry['collected'] * 100 / entry['expected'], 1) if entry['expected'] else 0

    data['fees'] = {
        'expected': expected,
        'collected': collected,
        'outstanding': outstanding,
        'students_with_balance': with_balance,
        'rate': round(collected * 100 / expected, 1) if expected else 0,
    }
    data['fees_by_class'] = list(by_class.values())

    # Academics
    data['class_performance'] = [{'class_name': r[0], 'average': float(r[1])} for r in class_rows]
    data['academics'] = {
        'school_average': float(school_avg) if school_avg is not None else None,
        'best_class': class_rows[0][0] if class_rows else None,
        'weakest_class': class_rows[-1][0] if len(class_rows) > 1 else None,
    }
    return data