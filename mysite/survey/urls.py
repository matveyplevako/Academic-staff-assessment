# -*- coding: utf-8 -*-

from django.urls import path


from survey.views import ConfirmView, IndexView, SurveyCompleted, SurveyDetail
from survey.views.survey_result import serve_result_csv

app_name = 'survey'

urlpatterns = [
    path('', IndexView.as_view(), name="survey-list"),
    path('<int:id>/', SurveyDetail.as_view(), name="survey-detail"),
    # path('csv/<int:primary_key>/', serve_result_csv, name="survey-result"),
    path("<int:id>/completed/", SurveyCompleted.as_view(), name="survey-completed"),
    # path("<int:id>-<int:step>/", SurveyDetail.as_view(), name="survey-detail-step"),
    path("confirm/<str:uuid>/", ConfirmView.as_view(), name="survey-confirmation"),

]
