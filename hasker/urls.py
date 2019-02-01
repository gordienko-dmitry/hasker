from django.urls import path, include
from questions import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.QuestionsList.as_view(), name='index'),
    path('rest/', include('api.urls')),
    path('hot', views.HotQuestionsList.as_view(), name='hot'),
    path('questions/', include('questions.urls')),
    path('users/', include('users.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
