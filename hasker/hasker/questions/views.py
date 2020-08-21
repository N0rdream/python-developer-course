from django.views import View
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, F, Count
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import HttpResponseRedirect

from .models import Question, Answer, Tag
from .forms import QuestionForm, AnswerForm


class QuestionAskView(CreateView):
    form_class = QuestionForm
    template_name = 'questions/ask.html'
    success_url = reverse_lazy('questions:list')

    def form_valid(self, form):
        form.instance.account = self.request.user
        form.save()
        tags = form.cleaned_data.get('tags')
        tags_objects = [Tag.objects.get_or_create(title=tag)[0] for tag in tags]
        form.instance.tags.add(*tags_objects)
        return super().form_valid(form)


class QuestionListView(ListView):
    paginate_by = 20
    template_name = 'questions/list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        q = self.request.GET.get('q')
        if q is None:
            return Question.non_hidden.select_related('account').order_by('-date_pub')
        else:
            q = q[:25]
        if q.startswith('tags:'):
            q = q[5:].strip()
            return Question.non_hidden.filter(
                tags__title=q
                ).select_related('account').order_by('-date_pub')
        return Question.non_hidden.filter(
            Q(title__icontains=q) | Q(content__icontains=q)
            ).select_related('account').annotate(
            uvoters=Count('u_voters'),
            dvoters=Count('d_voters')
            ).order_by(F('dvoters') - F('uvoters'), '-date_pub')


class AnswersDisplay(ListView):
    paginate_by = 2
    template_name = 'questions/discussion.html'
    context_object_name = 'answers'

    def get_queryset(self):
        return Answer.objects.filter(
            question__id=self.kwargs['pk']
            ).select_related('account').order_by('-date_pub')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = get_object_or_404(Question, pk=self.kwargs['pk'])
        context['form'] = AnswerForm()
        return context


class AnswerFormView(FormView):
    template_name = 'questions/discussion.html'
    form_class = AnswerForm

    def form_valid(self, form):
        question = Question.non_hidden.get(pk=self.kwargs['pk'])
        with transaction.atomic():
            form.instance.account = self.request.user
            form.instance.question = question
            form.save()
        question.account.send_email()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('questions:detail', kwargs={'pk': self.kwargs['pk']})


class QuestionDetail(View):
    def get(self, request, *args, **kwargs):
        view = AnswersDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = AnswerFormView.as_view()
        return view(request, *args, **kwargs)


def set_best_answer(request, id_a):
    answer = get_object_or_404(Answer, pk=id_a)
    answer.make_best()
    return HttpResponseRedirect(reverse('questions:detail', kwargs={'pk': answer.question_id}))


def clear_best_answer(request, id_q):
    question = get_object_or_404(Question, pk=id_q)
    question.clear_best()
    return HttpResponseRedirect(reverse('questions:detail', kwargs={'pk': question.id}))


def vote_question(request, id_q, up=True):
    question = get_object_or_404(Question, pk=id_q)
    if up:
        question.vote_up(request.user)
    else:
        question.vote_down(request.user)
    return HttpResponseRedirect(reverse('questions:detail', kwargs={'pk': question.id}))


def vote_up_question(request, id_q):
    return vote_question(request, id_q)


def vote_down_question(request, id_q):
    return vote_question(request, id_q, up=False)
     

def vote_answer(request, id_a, up=True):
    answer = Answer.objects.get(pk=id_a)
    if up:
        answer.vote_up(request.user)
    else:
        answer.vote_down(request.user)
    return HttpResponseRedirect(reverse('questions:detail', kwargs={'pk': answer.question_id}))


def vote_up_answer(request, id_a):
    return vote_answer(request, id_a)    


def vote_down_answer(request, id_a):
    return vote_answer(request, id_a, up=False)
