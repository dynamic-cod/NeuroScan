from __future__ import annotations

from celery import shared_task
from django.utils import timezone

from .models import Assessment, PerformanceMetric
from .ml_model.model_handler import ModelHandler


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_pending_assessments(self):
    handler = ModelHandler()
    qs = Assessment.objects.filter(stage=Assessment.STAGE_DETAILED, is_batch_processed=False)
    count = 0
    for assessment in qs.iterator():
        prediction = handler.predict(assessment.symptom_text,
                                    scores={
                                        "anxiety": assessment.anxiety_score or 0.0,
                                        "depression": assessment.depression_score or 0.0,
                                        "stress": assessment.stress_score or 0.0,
                                    })
        assessment.predicted_state = prediction["predicted_state"]
        assessment.risk_level = prediction["risk_level"]
        assessment.recommendation = prediction["recommendation"]
        assessment.is_batch_processed = True
        assessment.save(update_fields=[
            "predicted_state", "risk_level", "recommendation", "is_batch_processed", "updated_at"
        ])
        count += 1
    PerformanceMetric.objects.create(metric_name="batch_processed_assessments", metric_value=float(count))
    return count


@shared_task
def record_metric(metric_name: str, metric_value: float):
    PerformanceMetric.objects.create(metric_name=metric_name, metric_value=metric_value)


@shared_task
def daily_cleanup():
    # Placeholder for cleanup logic
    PerformanceMetric.objects.create(metric_name="daily_cleanup_run", metric_value=float(timezone.now().timestamp()))
