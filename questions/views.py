from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.shortcuts import redirect, render, get_object_or_404
from django.views import generic
from django.http import Http404
from django.urls import reverse_lazy
from .models import Question, Answer, vote_qa
from .forms import AskForm, AnswerForm
import hasker.settings as settings


class QuestionsList(generic.ListView):
    model = Question
    template_name = 'index.html'
    queryset = Question.objects.order_by("-pub_date", "-rank").all()
    paginate_by = settings.QUESTION_BATCH


class HotQuestionsList(generic.ListView):
    model = Question
    template_name = 'index.html'
    queryset = Question.objects.order_by("-rank", "-pub_date").all()
    paginate_by = settings.QUESTION_BATCH


class SearchQuestion(generic.ListView):
    model = Question
    template_name = 'search.html'
    paginate_by = settings.QUESTION_BATCH

    def get_queryset(self):
        return Question.get_search(self.request.GET.get("query").split())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_text'] = self.request.GET.get("query")
        return context


class AskQuestion(generic.FormView):
    model = Question
    form_class = AskForm
    template_name = 'ask.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        question = Question.create_question(self.request)
        return redirect(question.get_url())


class QuestionAnswer(generic.ListView):
    model = Answer
    template_name = 'question.html'
    paginate_by = settings.ANSWERS_BATCH

    def get_queryset(self):
        question_id = self.kwargs.get('question_id')
        return Answer.get_answers(question_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        right_answer = Answer.objects.filter(id=question.right_answer).first()
        is_authenticated = self.request.user.is_authenticated

        if is_authenticated:
            up_down_q = question.is_user_vote(self.request.user)
            up_down_a = Answer.get_votes(self.object_list, self.request.user)
        else:
            up_down_a = ""
            up_down_q = ""

        context['question'] = question
        context['right_answer'] = right_answer
        context['is_authenticated'] = is_authenticated
        context['up_down_q'] = up_down_q
        context['up_down_a'] = up_down_a
        return context

class CreateAnswer(generic.FormView):
    model = Answer
    form_class = AnswerForm
    template_name = 'question.html'

    def dispatch(self, request, *args, **kwargs):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        Answer.create_answer(self.request, question)
        return redirect(question.get_url())


class RightAnswer(LoginRequiredMixin, generic.FormView):
    """make answer right"""
    login_url = reverse_lazy('login')
    redirect_field_name =  reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        id = request.GET.get('id')
        id_answer = int(request.GET.get('answer_id'))
        question = get_object_or_404(Question, id=id)
        question.set_right_answer(id_answer, request.user)
        return redirect(question.get_url())


class Vote(LoginRequiredMixin, generic.FormView):
    """vote for auestion or answer"""

    login_url = reverse_lazy('login')
    redirect_field_name =  reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        if request.method != "POST":
            return Http404("BAD")
        id = request.POST.get("id")
        type_entity = request.POST.get("entity")
        up = request.POST.get("up") == "true"

        user_id = request.user.id
        rank, up_down = vote_qa(type_entity, id, up, user_id)
        template = "up_down_rank_right.html" if type_entity == "a" else "up_down_rank_question.html"

        if type_entity == "q":
            key = make_template_fragment_key('rightbar')
            cache.delete(key)

        return render(request, template,
                      context={"up": up, "up_down": up_down, "right": False, "rank": rank, "id": id})