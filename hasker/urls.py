"""hasker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from questions import views

urlpatterns = [
    path('', views.index_page, name='index'),
    path('rest/', include('api.urls')),
    path('hot', views.hot_questions, name='hot'),
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.logout_user, name='logout'),
    path('signup', views.SignUp.as_view(), name='signup'),
    path('profile', views.profile, name='profile'),
    path('', include('questions.urls'))
]
