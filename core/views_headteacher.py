from django.shortcuts import render, redirect
from .permissions import school_role_required
from core.services.headteacher import get_headteacher_dashboard_data  # Import your service logic safely

@school_role_required(allowed_roles=['HEADTEACHER'])
def headteacher_dashboard_view(request):
    """
    Main controller for the headteacher audit dashboard workspace.
    """
    # Capture chosen term parameters from request URL query strings string parameters (?term=X)
    selected_term_id = request.GET.get('term')
    
    # Process data matrices via your decoupled business services layer
    dashboard_data = get_headteacher_dashboard_data(selected_term_id)
    
    # Append styling titles for base.html layout shells
    dashboard_data['title'] = 'Headteacher Strategic Command Console'
    
    return render(request, 'core/headteacher/dashboard.html', dashboard_data)
