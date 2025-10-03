from django.db import models
from django.utils import timezone


class Assessment(models.Model):
    STAGE_INITIAL = "initial"
    STAGE_DETAILED = "detailed"
    STAGE_CHOICES = [
        (STAGE_INITIAL, "Initial"),
        (STAGE_DETAILED, "Detailed"),
    ]

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    user_identifier = models.CharField(max_length=255, db_index=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default=STAGE_INITIAL)

    # Scores and inputs
    symptom_text = models.TextField(blank=True)
    anxiety_score = models.FloatField(null=True, blank=True)
    depression_score = models.FloatField(null=True, blank=True)
    stress_score = models.FloatField(null=True, blank=True)

    # Prediction
    predicted_state = models.CharField(max_length=100, blank=True)
    risk_level = models.CharField(max_length=50, blank=True)
    recommendation = models.TextField(blank=True)

    # Tracking
    is_batch_processed = models.BooleanField(default=False)
    follow_up_scheduled = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Assessment({self.user_identifier}, {self.stage}, {self.created_at:%Y-%m-%d})"


class PerformanceMetric(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    metric_name = models.CharField(max_length=255)
    metric_value = models.FloatField()
    labels = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.metric_name}: {self.metric_value}"


class APIMetric(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    latency_ms = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.method} {self.endpoint} {self.status_code} ({self.latency_ms}ms)"


class FormMetric(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    form_name = models.CharField(max_length=255)
    submit_success = models.BooleanField(default=True)
    validation_errors = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return f"{self.form_name} success={self.submit_success}"
