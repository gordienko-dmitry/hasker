from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from .models import Question, Answer, vote_qa


@login_required(redirect_field_name=reverse_lazy('index'), login_url=reverse_lazy('login'))
def right_answer(request):
    """make answer right"""

    id = request.GET.get('id')
    id_answer = int(request.GET.get('answer_id'))
    try:
        question = Question.objects.get(id=id)
    except Question.DoesNotExist:
        return Http404("Bad request: Wrong question id")
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
