from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.session.get('user_id'):
                return redirect('/login/')
            if request.session.get('role') not in roles:
                return HttpResponseForbidden('You do not have access to this page.')
            return view(request, *args, **kwargs)
        return wrapper
    return decorator