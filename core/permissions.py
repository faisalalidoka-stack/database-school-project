from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def school_role_required(allowed_roles=[]):
    """
    Checks the role string inside your custom 'Users' model table to restrict workspace access.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            custom_user_id = request.session.get('user_id')
            custom_user_role = request.session.get('user_role')
            
            if not custom_user_id or not custom_user_role:
                return redirect('login')
                
            if custom_user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
                
            raise PermissionDenied("Access Denied: Your assigned role does not permit entry here.")
        return _wrapped_view
    return decorator
