from django.contrib import admin
from django.urls import path
from core.views_headteacher import headteacher_dashboard_view
from core.views import (
    login_view, logout_view, dashboard_view, 
    student_list_view, add_student_view, 
    marks_entry_view, fee_payments_view
)
# Safe clean import pointing directly to our newly generated file
from core.views_staff import (
    teacher_dashboard, enter_marks,
    dos_dashboard, bursar_dashboard, nurse_dashboard
)

urlpatterns = [
    path('', login_view, name='root_login'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('students/', student_list_view, name='student_list'),
    path('students/add/', add_student_view, name='add_student'),
    path('marks/', marks_entry_view, name='marks_entry'),     
    path('fees/', fee_payments_view, name='fee_payments'),    
    path('admin/', admin.site.urls),
    path('headteacher/', headteacher_dashboard_view, name='headteacher_dashboard'),

    # Cleaned Staff Workspace Routing URLs
    path('teacher/', teacher_dashboard, name='teacher_dashboard'),
    path('teacher/marks/<int:class_id>/', enter_marks, name='enter_marks'),
    path('dos/', dos_dashboard, name='dos_dashboard'),
    path('bursar-workspace/', bursar_dashboard, name='bursar_dashboard'),
    path('nurse-workspace/', nurse_dashboard, name='nurse_dashboard'),
]
