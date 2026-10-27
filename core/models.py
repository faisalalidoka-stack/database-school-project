from django.db import models
from django.contrib.auth.models import User

class Classes(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(unique=True, max_length=20)
    class_teacher = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'classes'


class Eligibility(models.Model):
    eligibility_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('Students', models.DO_NOTHING)
    term = models.ForeignKey('Terms', models.DO_NOTHING)
    meal_eligible = models.IntegerField()
    exam_eligible = models.IntegerField()
    date_generated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eligibility'
        unique_together = (('student', 'term'),)


class FeePayments(models.Model):
    payment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('Students', models.DO_NOTHING)
    term = models.ForeignKey('Terms', models.DO_NOTHING)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(blank=True, null=True)
    receipt_no = models.CharField(unique=True, max_length=30)
    received_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='received_by')

    class Meta:
        managed = False
        db_table = 'fee_payments'


class FeeStructure(models.Model):
    fee_structure_id = models.AutoField(primary_key=True)
    class_field = models.ForeignKey(Classes, models.DO_NOTHING, db_column='class_id')
    term = models.ForeignKey('Terms', models.DO_NOTHING)
    amount_required = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'fee_structure'
        unique_together = (('class_field', 'term'),)


class Marks(models.Model):
    mark_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('Students', models.DO_NOTHING)
    subject = models.ForeignKey('Subjects', models.DO_NOTHING)
    term = models.ForeignKey('Terms', models.DO_NOTHING)
    teacher = models.ForeignKey('Users', models.DO_NOTHING)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    date_recorded = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'marks'
        unique_together = (('student', 'subject', 'term'),)


class ReportCards(models.Model):
    report_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('Students', models.DO_NOTHING)
    term = models.ForeignKey('Terms', models.DO_NOTHING)
    total_score = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    grade = models.CharField(max_length=10, blank=True, null=True)
    class_position = models.IntegerField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    generated_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'report_cards'
        unique_together = (('student', 'term'),)


class Students(models.Model):
    student_id = models.AutoField(primary_key=True)
    admission_no = models.CharField(unique=True, max_length=30)
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_contact = models.CharField(max_length=30, blank=True, null=True)
    class_field = models.ForeignKey(Classes, models.DO_NOTHING, db_column='class_id')

    class Meta:
        managed = False
        db_table = 'students'

    def __str__(self):
        return self.full_name


class Subjects(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=80)
    class_field = models.ForeignKey(Classes, models.DO_NOTHING, db_column='class_id')

    class Meta:
        managed = False
        db_table = 'subjects'


class Terms(models.Model):
    term_id = models.AutoField(primary_key=True)
    term_name = models.CharField(max_length=30)
    academic_year = models.CharField(max_length=4)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'terms'
        unique_together = (('term_name', 'academic_year'),)

    def __str__(self):
        return f"{self.term_name} ({self.academic_year})"


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    username = models.CharField(unique=True, max_length=50)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=30)  # Values: 'HEADTEACHER', 'TEACHER', 'DOS', 'BURSAR', 'NURSE'
    is_active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'users'

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class MedicalLogs(models.Model):
    log_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Students, models.DO_NOTHING, db_column='student_id')
    term = models.ForeignKey(Terms, models.DO_NOTHING, db_column='term_id')
    symptoms = models.TextField()
    treatment_given = models.TextField()
    visit_date = models.DateTimeField(auto_now_add=True)
    logged_by = models.ForeignKey(Users, models.DO_NOTHING, db_column='user_id')

    class Meta:
        managed = True  # Instructs Django to physically create this missing table in your MySQL DB
        db_table = 'medical_logs'
# =========================================================================
# 🆕 HEADTEACHER SPEC EXTRA DATA SCHEMAS (Managed = True)
# =========================================================================

class AuditLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    performed_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='user_id')
    action_type = models.CharField(max_length=50) # e.g., 'ELIGIBILITY_OVERRIDE', 'STAFF_RESET'
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'audit_log'


class FeeWaivers(models.Model):
    waiver_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('Students', models.DO_NOTHING, db_column='student_id')
    term = models.ForeignKey('Terms', models.DO_NOTHING, db_column='term_id')
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, default='PENDING') # 'PENDING', 'APPROVED', 'REJECTED'
    reviewed_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='reviewed_by', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'fee_waivers'


# Since ReportCards is an auto-generated unmanaged table from your schema, 
# we create a specialized Approval status extension table to track Headteacher flags 
# without altering your raw 'report_cards' structural layout directly.
class ReportCardApprovals(models.Model):
    approval_id = models.AutoField(primary_key=True)
    report = models.ForeignKey('ReportCards', models.DO_NOTHING, db_column='report_id')
    status = models.CharField(max_length=20, default='PENDING') # 'PENDING', 'APPROVED', 'BLOCKED'
    headteacher_remark = models.TextField(blank=True, null=True)
    reviewed_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'report_card_approvals'
