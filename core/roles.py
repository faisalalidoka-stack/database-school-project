# The single place that decides what each database role means in the code.
# Everything else (login, guards, menus) uses these short codes.

ROLE_CODES = {
    'headteacher': 'HEADTEACHER',
    'deputy_headteacher': 'DEPUTY',
    'director_of_studies': 'DOS',
    'dos': 'DOS',
    'class_teacher': 'TEACHER',
    'teacher': 'TEACHER',
    'bursar': 'BURSAR',
    'nurse': 'NURSE',
}

# Where each role lands after login (URL names from urls.py)
HOME_PAGES = {
    'HEADTEACHER': 'headteacher_dashboard',
    'TEACHER': 'teacher_dashboard',
    'DOS': 'dos_dashboard',
    'BURSAR': 'bursar_dashboard',
    'NURSE': 'nurse_dashboard',
}


def role_code(db_role):
    """Turn a role from the users table into a code, or None if unknown."""
    return ROLE_CODES.get((db_role or '').strip().lower())