from django.contrib import admin
from django.urls import path, re_path, include
from questions import views

urlpatterns = [
    path('search', views.search_page, name='search'),
    path('ask', views.ask, name='ask'),
    path('right_answer', views.right_answer, name='right_answer'),
    path('vote', views.vote, name='vote'),

    re_path(r'question/(?P<question_id>\d+)',
            views.get_question_post_answer, name="question"),

    re_path(r'.*', views.error_404, name='not_found'),
]
