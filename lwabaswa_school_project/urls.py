from django.contrib import admin
from django.urls import path
from core.views import (
    login_view, logout_view, dashboard_view, 
    student_list_view, add_student_view, 
    marks_entry_view, fee_payments_view
)

urlpatterns = [
    path('', login_view, name='root_login'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('students/', student_list_view, name='student_list'),
    path('students/add/', add_student_view, name='add_student'),
    path('marks/', marks_entry_view, name='marks_entry'),     # New Marks Route
    path('fees/', fee_payments_view, name='fee_payments'),    # New Fees Route
    path('admin/', admin.site.urls),
]
