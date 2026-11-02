from django.contrib import admin
from .models import (
    Course, TeacherProfile, Discipline, ClassGroup, ClassOffering,
    EvaluationCycle, EvaluationDimension, EvaluationCriterion,
    EvaluationReceipt, EvaluationResponse, DisposableEvaluationToken
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'modality', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('modality',)

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'academic_title', 'department')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'department')
    list_filter = ('academic_title', 'department')

@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'course', 'workload_hours')
    search_fields = ('name', 'code', 'course__name')
    list_filter = ('course',)

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'shift', 'year', 'semester')
    search_fields = ('name', 'course__name')
    list_filter = ('shift', 'year', 'semester', 'course')
    filter_horizontal = ('students',)

@admin.register(ClassOffering)
class ClassOfferingAdmin(admin.ModelAdmin):
    list_display = ('discipline', 'teacher', 'class_group', 'academic_period', 'is_active')
    search_fields = ('discipline__name', 'teacher__user__first_name', 'teacher__user__last_name', 'class_group__name')
    list_filter = ('academic_period', 'is_active', 'class_group__course')

class EvaluationCriterionInline(admin.TabularInline):
    model = EvaluationCriterion
    extra = 1

@admin.register(EvaluationDimension)
class EvaluationDimensionAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'weight')
    inlines = [EvaluationCriterionInline]

@admin.register(EvaluationCriterion)
class EvaluationCriterionAdmin(admin.ModelAdmin):
    list_display = ('dimension', 'order', 'title', 'min_score', 'max_score')
    list_filter = ('dimension',)

@admin.register(EvaluationCycle)
class EvaluationCycleAdmin(admin.ModelAdmin):
    list_display = ('title', 'academic_period', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'academic_period')

@admin.register(EvaluationReceipt)
class EvaluationReceiptAdmin(admin.ModelAdmin):
    list_display = ('student', 'offering', 'cycle', 'receipt_hash', 'completed_at')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'receipt_hash')
    list_filter = ('cycle', 'offering__class_group')
    readonly_fields = ('student', 'offering', 'cycle', 'receipt_hash', 'completed_at')

@admin.register(EvaluationResponse)
class EvaluationResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'offering', 'cycle', 'overall_score', 'moderation_status', 'submitted_at')
    list_filter = ('moderation_status', 'cycle', 'offering__teacher')
    search_fields = ('offering__discipline__name', 'comment')
    readonly_fields = ('offering', 'cycle', 'overall_score', 'criteria_scores', 'dimension_scores', 'submitted_at')

@admin.register(DisposableEvaluationToken)
class DisposableEvaluationTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'offering', 'cycle', 'is_used', 'used_at', 'created_at')
    list_filter = ('is_used', 'cycle', 'offering__class_group')
    search_fields = ('token',)
