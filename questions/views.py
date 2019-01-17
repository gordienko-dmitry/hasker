from http import HTTPStatus

from django.contrib.auth import logout, views, forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, render_to_response
from django.views import generic
from django.views.decorators.http import require_GET
from django.urls import reverse_lazy
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from django.template.response import TemplateResponse

from .models import Question, Answer, UserWithAvatar, vote_qa
from .forms import SignUpForm, UserProfileForm
import hasker.settings as settings


class Login(views.LoginView):
    template_name = 'login.html'
    redirect_field_name = 'profile'
    authentication_form = forms.AuthenticationForm
    redirect_authenticated_user = True

    #trend_questions, _ = Question.get_questions(True, 1)
    #extra_context = {"trend_questions": trend_questions}


class SignUp(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    #trend_questions, _ = Question.get_questions(True, 1)
    #extra_context = {"trend_questions": trend_questions}


def page_strucks(page, count):
    """function for solving prev pages and next pages
    for pagination on current page"""

    num = settings.NUMBER_PAGES
    n = (num - 1) // 2
    begin_page = max(page - n, 1)
    prev = [i for i in range(begin_page, page)]
    end_page = min(count + 1, page + num - len(prev))
    next = [i for i in range(page + 1, end_page)]
    return prev, next


def index_page(request):
    """Main site page"""

    page = int(request.GET.get("page", 1))
    questions, count_pages = Question.get_questions(False, page)
    prev_pages, next_pages = page_strucks(page, count_pages)
    extends = 'blank.html' if request.is_ajax() else 'base.html'

    return TemplateResponse(request=request, template='index.html',
                            context={"questions": questions,
                                     "page": page,
                                     "next_pages": next_pages,
                                     "prev_pages": prev_pages,
                                     "count": count_pages,
                                     "extends": extends})


def hot_questions(request):
    """index with high rank questions"""
    page = int(request.GET.get("page", 1))
    questions, count_pages = Question.get_questions(True, page)
    prev_pages, next_pages = page_strucks(page, count_pages)
    extends = 'base.html'
    if request.is_ajax():
        extends = 'blank.html'

    return TemplateResponse(request, 'index.html',
                            context={"questions": questions,
                                     "page": page,
                                     "next_pages": next_pages,
                                     "prev_pages": prev_pages,
                                     "count": count_pages,
                                     'extends': extends})


def search_page(request):
    """result of searching"""

    page = int(request.GET.get("page", 1))
    query = request.GET.get("query")
    search_query = query.split()
    if search_query:
        questions, count_pages = Question.get_search(search_query, page)
    else:
        questions = []
        count_pages = 0
    prev_pages, next_pages = page_strucks(page, count_pages)
    extends = 'base.html'
    if request.is_ajax():
        extends = 'blank.html'

    return TemplateResponse(request, 'search.html',
                            context={"questions": questions,
                                     "page": page,
                                     "next_pages": next_pages,
                                     "prev_pages": prev_pages,
                                     "count": count_pages,
                                     'extends': extends,
                                     'search_text': query})


@require_GET
def logout_user(request):
    logout(request)
    return redirect(reverse_lazy('index'))


@login_required(redirect_field_name=reverse_lazy('index'), login_url=reverse_lazy('login'))
def profile(request):
    """profile=setting user"""
    if request.method == 'GET':
        trend_questions, _ = Question.get_questions(True, 1)
        return TemplateResponse(request, "profile.html", context={})
    elif request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = UserWithAvatar.get_user(user_id=request.user.id)
            user_profile.update_profile(request.POST.get("email"),
                                        request.FILES.get("avatar"))
            return redirect(reverse_lazy('profile'))

        else:
            return TemplateResponse(request, "profile.html", context={"form": form})


@login_required(redirect_field_name=reverse_lazy('index'), login_url=reverse_lazy('login'))
def ask(request):
    """ask a question"""

    if request.method == 'GET':
        return TemplateResponse(request, "ask.html", context={})
    else:
        question = Question.create_question(request)
        return redirect("/question/{}".format(question.id))


def get_question_post_answer(request, question_id):
    """page of question with answers
    authorized users can post answer"""

    try:
        question = Question.objects.get(id=question_id)
    except:
        return redirect('404')

    if request.method == "POST":
        Answer.create_answer(request, question)
        request.method = "GET"

    page = request.GET.get('page', 1)
    answers, count_pages = Answer.get_answers(question, page)
    is_authenticated = request.user.is_authenticated
    prev_pages, next_pages = page_strucks(page, count_pages)
    if is_authenticated:
        up_down_q = question.is_user_vote(request.user)
        up_down_a = Answer.get_votes(answers, request.user)
    else:
        up_down_a = ""
        up_down_q = ""

    try:
        right_answer = Answer.objects.get(id=question.right_answer)
    except Answer.DoesNotExist:
        right_answer = None

    return TemplateResponse(request, "question.html",
                            context={"answers": answers, "question": question, "page": page,
                                     "up_down_q": up_down_q, "up_down_a": up_down_a, "right_answer": right_answer,
                                     "is_authenticated": is_authenticated, "count": count_pages,
                                     "next_pages": next_pages,
                                     "prev_pages": prev_pages,
                                     })


@login_required(redirect_field_name=reverse_lazy('index'), login_url=reverse_lazy('login'))
def right_answer(request):
    """make answer right"""

    id = request.GET.get('id')
    id_answer = int(request.GET.get('answer_id'))
    try:
        question = Question.objects.get(id=id)
    except Question.DoesNotExist:
        return error_404(request)
    question.set_right_answer(id_answer, request.user)
    return redirect(question.get_url())


@login_required(redirect_field_name=reverse_lazy('index'), login_url=reverse_lazy('login'))
def vote(request):
    """vote for auestion or answer"""

    type_entity = request.POST.get("entity")
    id = request.POST.get("id")
    up = request.POST.get("up") == "true"

    user_id = request.user.id
    rank, up_down = vote_qa(type_entity, id, up, user_id)
    template = "up_down_rank_right.html" if type_entity == "a" else "up_down_rank_question.html"

    if type_entity == "q":
        key = make_template_fragment_key('rightbar')
        cache.delete(key)

    return render(request, template,
                  context={"up": up, "up_down": up_down, "right": False, "rank": rank, "id": id})


def error_404(request):
    """404 page"""
    response = render(request, '404.html', {'error': True})
    response.status_code = HTTPStatus.NOT_FOUND.value
    return response
