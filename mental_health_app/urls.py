from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("assessment/", views.self_assessment, name="self_assessment"),
    path("assessment/detailed/", views.detailed_assessment, name="detailed_assessment"),
    path("assessment/result/", views.assessment_result, name="assessment_result"),
    path("resources/", views.resources, name="resources"),
]
