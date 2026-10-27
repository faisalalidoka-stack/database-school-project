from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .permissions import school_role_required
from core.models import Users, Classes, FeeStructure, Terms, FeeWaivers, ReportCardApprovals, ReportCards, Eligibility, Students, AuditLog
from core.services.headteacher import get_headteacher_dashboard_data

@school_role_required(allowed_roles=['HEADTEACHER'])
def headteacher_dashboard_view(request):
    current_admin = get_object_or_404(Users, pk=request.session.get('user_id'))
    
    if request.method == 'POST':
        action = request.POST.get('action')

        # Criteria 2: Staff Management Action
        if action == 'register_staff':
            Users.objects.create(
                full_name=request.POST.get('full_name'),
                username=request.POST.get('username'),
                password_hash=request.POST.get('password'),
                role=request.POST.get('role').upper(),
                is_active=1
            )
            AuditLog.objects.create(performed_by=current_admin, action_type='STAFF_CREATE', description=f"Registered staff account: {request.POST.get('username')}")
            messages.success(request, "Staff profile deployed successfully.")

        elif action == 'reset_password':
            staff = get_object_or_404(Users, pk=request.POST.get('user_id'))
            staff.password_hash = request.POST.get('new_password')
            staff.save()
            AuditLog.objects.create(performed_by=current_admin, action_type='STAFF_PASSWORD_RESET', description=f"Reset password for staff: {staff.username}")
            messages.success(request, "Password credentials updated.")

        # Criteria 3: School Configuration Setup
        elif action == 'create_term':
            Terms.objects.create(
                term_name=request.POST.get('term_name'),
                academic_year=request.POST.get('academic_year'),
                start_date=request.POST.get('start_date') or None,
                end_date=request.POST.get('end_date') or None
            )
            messages.success(request, "New academic term cycle registered.")

        # Criteria 4: Fees Waiver Review Approval
        elif action == 'review_waiver':
            waiver = get_object_or_404(FeeWaivers, pk=request.POST.get('waiver_id'))
            decision = request.POST.get('decision') # 'APPROVED' or 'REJECTED'
            waiver.status = decision
            waiver.reviewed_by = current_admin
            waiver.save()
            AuditLog.objects.create(performed_by=current_admin, action_type='WAIVER_DECISION', description=f"Waiver {decision} for student ID: {waiver.student_id}")
            messages.success(request, f"Fee waiver request review status set to: {decision}")

        # Criteria 4: Manual Student Profile Eligibility Overrides
        elif action == 'override_eligibility':
            student_id = request.POST.get('student_id')
            term_id = request.POST.get('term_id')
            reason_str = request.POST.get('override_reason')
            
            elig, created = Eligibility.objects.update_or_create(
                student_id=student_id, term_id=term_id,
                defaults={'meal_eligible': 1, 'exam_eligible': 1}
            )
            AuditLog.objects.create(performed_by=current_admin, action_type='ELIGIBILITY_OVERRIDE', description=f"Overrode eligibility for student #{student_id}. Reason: {reason_str}")
            messages.success(request, "Eligibility parameters successfully manually overridden and logged.")

        # Criteria 5: Academics Report Cards Approvals
        elif action == 'review_report':
            report_id = request.POST.get('report_id')
            decision = request.POST.get('decision') # 'APPROVED' or 'BLOCKED'
            remark_text = request.POST.get('headteacher_remark','')
            
            ReportCardApprovals.objects.update_or_create(
                report_id=report_id,
                defaults={'status': decision, 'headteacher_remark': remark_text}
            )
            messages.success(request, f"Report card item status marked as {decision}.")

        return redirect('headteacher_dashboard')

    # Get dashboard analytical statistics data context
    selected_term_id = request.GET.get('term')
    context = get_headteacher_dashboard_data(selected_term_id)
    context['title'] = 'Headteacher Strategic Command Console'
    
    # Context lists for operational sub-panels
    context['pending_waivers'] = FeeWaivers.objects.filter(status='PENDING')
    context['unapproved_reports'] = ReportCards.objects.all()[:10]
    context['all_staff_members'] = Users.objects.all()
    context['all_classes'] = Classes.objects.all()
    context['audit_logs'] = AuditLog.objects.all().order_by('-timestamp')[:15]
    
    return render(request, 'core/headteacher/dashboard.html', context)
