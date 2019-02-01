from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views import generic
from django.urls import reverse_lazy
from .models import Question, Answer
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
        return redirect("/questions/question/{}".format(question.id))


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

    def form_valid(self, form):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        Answer.create_answer(self.request, question)
        return redirect("/questions/question/{}".format(question.id))

    def dispatch(self, request, *args, **kwargs):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        Answer.create_answer(self.request, question)
        return redirect("/questions/question/{}".format(question.id))
