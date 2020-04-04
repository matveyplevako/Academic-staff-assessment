# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from survey.models import Survey


class SurveyCompleted(LoginRequiredMixin, TemplateView):

    template_name = "completed.html"

    def get_context_data(self, **kwargs):
        context = {}
        survey = get_object_or_404(Survey, is_published=True, id=kwargs["id"])
        context["survey"] = survey
        return context
