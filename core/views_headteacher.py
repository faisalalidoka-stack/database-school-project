from django.shortcuts import render
from .permissions import role_required
from .services import headteacher as ht


@role_required('headteacher')
def headteacher_dashboard_view(request):
    data = ht.get_dashboard_data(request.GET.get('term'))
    return render(request, 'core/headteacher/dashboard.html', {'data': data})