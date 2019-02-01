from django.contrib.auth import views
from django.shortcuts import redirect
from django.views import generic
from django.urls import reverse_lazy
from .forms import SignUpForm, UserProfileForm, LoginForm
from users.models import UserWithAvatar


class Login(views.LoginView):
    template_name = 'login.html'
    redirect_field_name = 'profile'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class SignUp(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


class Logout(views.LogoutView):
    next_page = reverse_lazy('login')


class Profile(generic.FormView):
    model = UserWithAvatar
    form_class = UserProfileForm
    template_name = 'profile.html'

    def get_initial(self):
        return {'email': self.request.user.email}

    def form_valid(self, form):
        user_profile = UserWithAvatar.get_user(user_id=self.request.user.id)
        user_profile.update_profile(self.request.POST.get("email"),
                                    self.request.FILES.get("avatar"))
        return redirect(reverse_lazy('profile'))
