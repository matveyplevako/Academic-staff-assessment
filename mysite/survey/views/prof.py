from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, \
    DeleteView
from django.views.generic.base import TemplateResponseMixin, View
from django.shortcuts import render, redirect, get_object_or_404
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.forms.models import modelform_factory
from collections import Counter
from django.http import Http404

from ..forms import CategoryFormSet

from ..models import Survey, Category, Question


class OwnerMixin:
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        if self.request.user.username == 'doe':
            return qs.all()
        else:
            return qs.filter(owner=self.request.user)


class OwnerSurveyMixin(OwnerMixin, LoginRequiredMixin):
    model = Survey
    fields = ['name', 'description', 'publish_date', 'expire_date']
    success_url = reverse_lazy('manage_survey_list')


class ManageSurveyListView(PermissionRequiredMixin, OwnerSurveyMixin, ListView):
    permission_required = 'survey.add_survey'
    template_name = 'survey/list.html'


class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerSurveyEditMixin(OwnerSurveyMixin, OwnerEditMixin):
    # fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('survey:manage_survey_list')
    template_name = 'survey/form.html'


class SurveyCreateView(PermissionRequiredMixin,
                       OwnerSurveyEditMixin,
                       CreateView):
    permission_required = 'survey.add_survey'


class SurveyUpdateView(PermissionRequiredMixin,
                       OwnerSurveyEditMixin,
                       UpdateView):
    permission_required = 'survey.change_survey'


class SurveyDeleteView(PermissionRequiredMixin,
                       OwnerSurveyMixin,
                       DeleteView):
    template_name = 'survey/delete.html'
    success_url = reverse_lazy('survey:manage_survey_list')
    permission_required = 'survey.delete_survey'


class SurveyCategoryUpdateView(TemplateResponseMixin, View):
    template_name = 'survey/formset.html'
    survey = None

    def get_formset(self, data=None):
        return CategoryFormSet(instance=self.survey, data=data)

    def dispatch(self, request, pk):
        self.survey = get_object_or_404(Survey,
                                        id=pk,
                                        owner=request.user)
        return super(SurveyCategoryUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'survey': self.survey,
                                        'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('survey:manage_survey_list')
        return self.render_to_response({'survey': self.survey,
                                        'formset': formset})


class CategoryQuestionListView(TemplateResponseMixin, View):
    template_name = 'survey/question_list.html'

    def get(self, request, category_id):
        category = get_object_or_404(Category,
                                     id=category_id,
                                     survey__owner=request.user)

        return self.render_to_response({'category': category})


class CategoryOrderView(CsrfExemptMixin,
                        JsonRequestResponseMixin,
                        View):
    def post(self, request):
        for _id, order in self.request_json.items():
            Category.objects.filter(id=_id,
                                    survey__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class QuestionOrderView(CsrfExemptMixin,
                        JsonRequestResponseMixin,
                        View):
    def post(self, request):
        for _id, order in self.request_json.items():
            Question.objects.filter(id=_id,
                                    survey__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class QuestionCreateUpdateView(TemplateResponseMixin, View):
    category = None
    survey = None
    model = Question
    obj = None
    template_name = 'survey/create_question.html'

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'category',
                                                 'survey',
                                                 'created'])
        return Form(*args, **kwargs)

    def dispatch(self, request, category_id, id=None):
        self.category = get_object_or_404(Category,
                                          id=category_id,
                                          survey__owner=request.user)
        self.survey = self.category.survey
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         survey__owner=request.user)
        return super(QuestionCreateUpdateView,
                     self).dispatch(request, category_id, id)

    def get(self, request, category_id, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, category_id, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.survey = self.survey
            obj.category = self.category
            obj.owner = request.user
            obj.save()
            return redirect('survey:category_question_list', self.category.id)

        return self.render_to_response({'form': form,
                                        'object': self.obj})


class QuestionDeleteView(View):

    def post(self, request, pk):
        question = get_object_or_404(Question,
                                     id=pk,
                                     survey__owner=request.user)
        category = question.category
        question.delete()
        return redirect('survey:category_question_list', category.id)


class SurveyResults(TemplateResponseMixin, View):
    template_name = 'survey_results.html'

    def get(self, request, survey_id):
        survey = get_object_or_404(Survey,
                                   id=survey_id)
        if request.user != survey.owner and request.user.username != "doe":
            raise Http404(f"{request.user.username} is not allowed to view results of this survey")

        for_pie_chart = []
        pie_questions = survey.questions.filter(type__in=[Question.RADIO, Question.SELECT, Question.SELECT_MULTIPLE])
        for q in pie_questions:
            choices = q.choices.split(",")
            ans_list = q.answers_as_text
            if q.type == Question.SELECT_MULTIPLE:
                rep = []
                for elem in ans_list:
                    elem = elem[1:-1]
                    for item in elem.split(","):
                        item = item.strip()[1:-1]
                        rep.append(item)
                ans_list = rep
            count_ans = Counter(ans_list)
            count_choices = [count_ans[choice] for choice in choices]
            for_pie_chart.append([q.text, choices, count_choices])

        other_questions = survey.questions.exclude(type__in=[Question.RADIO, Question.SELECT, Question.SELECT_MULTIPLE])
        return self.render_to_response({'survey': survey,
                                        'for_pie_chart': for_pie_chart,
                                        'other_questions': other_questions})
