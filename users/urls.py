from django.contrib.auth.decorators import login_required
from django.urls import path
from users import views

urlpatterns = [
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('signup', views.SignUp.as_view(), name='signup'),
    path('profile', login_required(views.Profile.as_view()), name='profile'),
]
