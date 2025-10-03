from __future__ import annotations

import time
from typing import Any, Dict

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import InitialAssessmentForm, DetailedAssessmentForm
from .models import Assessment, FormMetric
from .ml_model.model_handler import ModelHandler
from .ml_model.exceptions import ModelNotLoadedError, InferenceError


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


def self_assessment(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = InitialAssessmentForm(request.POST)
        if form.is_valid():
            assessment = Assessment.objects.create(
                user_identifier=form.cleaned_data["user_identifier"],
                symptom_text=form.cleaned_data.get("symptom_text", ""),
                stage=Assessment.STAGE_INITIAL,
            )
            request.session["assessment_id"] = assessment.id
            FormMetric.objects.create(form_name="InitialAssessmentForm", submit_success=True)
            return redirect(reverse("detailed_assessment"))
        else:
            FormMetric.objects.create(
                form_name="InitialAssessmentForm", submit_success=False, validation_errors=form.errors.get_json_data()
            )
    else:
        form = InitialAssessmentForm()
    return render(request, "self_assessment.html", {"form": form})


def detailed_assessment(request: HttpRequest) -> HttpResponse:
    assessment_id = request.session.get("assessment_id")
    if not assessment_id:
        return redirect(reverse("self_assessment"))

    assessment = Assessment.objects.get(id=assessment_id)

    if request.method == "POST":
        form = DetailedAssessmentForm(request.POST)
        if form.is_valid():
            assessment.anxiety_score = form.cleaned_data["anxiety_score"]
            assessment.depression_score = form.cleaned_data["depression_score"]
            assessment.stress_score = form.cleaned_data["stress_score"]
            assessment.stage = Assessment.STAGE_DETAILED

            handler = ModelHandler()
            try:
                prediction = handler.predict(
                    assessment.symptom_text,
                    scores={
                        "anxiety": assessment.anxiety_score,
                        "depression": assessment.depression_score,
                        "stress": assessment.stress_score,
                    },
                )
                assessment.predicted_state = prediction["predicted_state"]
                assessment.risk_level = prediction["risk_level"]
                assessment.recommendation = prediction["recommendation"]
            except (ModelNotLoadedError, InferenceError):
                assessment.predicted_state = "unavailable"
                assessment.risk_level = "unknown"
                assessment.recommendation = "Results are temporarily unavailable. Please try again later."
            assessment.save()
            FormMetric.objects.create(form_name="DetailedAssessmentForm", submit_success=True)
            return redirect(reverse("assessment_result"))
        else:
            FormMetric.objects.create(
                form_name="DetailedAssessmentForm", submit_success=False, validation_errors=form.errors.get_json_data()
            )
    else:
        form = DetailedAssessmentForm()

    return render(request, "detailed_assessment.html", {"form": form, "assessment": assessment})


def assessment_result(request: HttpRequest) -> HttpResponse:
    assessment_id = request.session.get("assessment_id")
    if not assessment_id:
        return redirect(reverse("self_assessment"))

    assessment = Assessment.objects.get(id=assessment_id)
    context: Dict[str, Any] = {
        "assessment": assessment,
    }
    return render(request, "assessment_result.html", context)


def resources(request: HttpRequest) -> HttpResponse:
    return render(request, "resources.html")
