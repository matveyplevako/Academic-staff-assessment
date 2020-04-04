# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from survey.models.response import Response


class ConfirmView(LoginRequiredMixin, TemplateView):

    template_name = "confirm.html"

    def get_context_data(self, **kwargs):
        context = super(ConfirmView, self).get_context_data(**kwargs)
        context["uuid"] = kwargs["uuid"]
        context["response"] = Response.objects.get(interview_uuid=kwargs["uuid"])
        return context
