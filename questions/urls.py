from django.contrib.auth.decorators import login_required
from django.urls import path, re_path
from questions import views


urlpatterns = [
    path('search', views.SearchQuestion.as_view(), name='search'),
    path('ask', login_required(views.AskQuestion.as_view()), name='ask'),
    path('right_answer', views.RightAnswer.as_view(), name='right_answer'),
    path('vote', views.Vote.as_view(), name='vote'),

    re_path(r'question/(?P<question_id>\d+)',
            views.QuestionAnswer.as_view(), name="question"),
    re_path(r'answer/(?P<question_id>\d+)',
            login_required(views.CreateAnswer.as_view()), name="new_answer"),

]