# -*- coding: utf-8 -*-

from django.urls import path

from survey.views import ConfirmView, IndexView, SurveyCompleted, SurveyDetail
from survey.views import ManageSurveyListView, SurveyCreateView, SurveyUpdateView
from survey.views import SurveyDeleteView, SurveyCategoryUpdateView, QuestionCreateUpdateView
from survey.views import CategoryOrderView, QuestionOrderView, CategoryQuestionListView
from survey.views import QuestionDeleteView, SurveyResults
from survey.views.survey_result import serve_result_csv

app_name = 'survey'

urlpatterns = [
    path('', IndexView.as_view(), name="survey-list"),
    path('<int:id>/', SurveyDetail.as_view(), name="survey-detail"),
    # path('csv/<int:primary_key>/', serve_result_csv, name="survey-result"),
    path("<int:id>/completed/", SurveyCompleted.as_view(), name="survey-completed"),
    # path("<int:id>-<int:step>/", SurveyDetail.as_view(), name="survey-detail-step"),
    path("confirm/<str:uuid>/", ConfirmView.as_view(), name="survey-confirmation"),

    path('mine/',
         ManageSurveyListView.as_view(),
         name='manage_survey_list'),
    path('create/',
         SurveyCreateView.as_view(),
         name='survey_create'),
    path('<pk>/edit/',
         SurveyUpdateView.as_view(),
         name='survey_edit'),
    path('<pk>/delete/',
         SurveyDeleteView.as_view(),
         name='survey_delete'),
    path('<survey_id>/results/',
         SurveyResults.as_view(),
         name='survey_results'),
    path('<pk>/category/',
         SurveyCategoryUpdateView.as_view(),
         name='survey_category_update'),
    path('category/order/',
         CategoryOrderView.as_view(),
         name='category_order'),
    path('content/order/',
         QuestionOrderView.as_view(),
         name='question_order'),
    path('module/<int:category_id>/content/<id>/',
         QuestionCreateUpdateView.as_view(),
         name='category_question_update'),
    path('content/<int:id>/delete/',
         QuestionDeleteView.as_view(),
         name='category_question_delete'),
    path('category/<int:category_id>/',
         CategoryQuestionListView.as_view(),
         name='category_question_list'),
    path('module/<int:category_id>/question/create/',
         QuestionCreateUpdateView.as_view(),
         name='category_question_create'),
]
