from django.contrib import admin
from .models import Assessment, PerformanceMetric, APIMetric, FormMetric


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("user_identifier", "stage", "predicted_state", "risk_level", "created_at")
    list_filter = ("stage", "created_at", "risk_level")
    search_fields = ("user_identifier", "predicted_state")


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ("metric_name", "metric_value", "created_at")
    list_filter = ("metric_name",)


@admin.register(APIMetric)
class APIMetricAdmin(admin.ModelAdmin):
    list_display = ("endpoint", "method", "status_code", "latency_ms", "created_at")
    list_filter = ("endpoint", "status_code", "method")


@admin.register(FormMetric)
class FormMetricAdmin(admin.ModelAdmin):
    list_display = ("form_name", "submit_success", "created_at")
    list_filter = ("form_name", "submit_success")
