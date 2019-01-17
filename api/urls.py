
from django.urls import path, re_path, include
from rest_framework_jwt.views import obtain_jwt_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from . import views
schema_view = get_schema_view(
   openapi.Info(
      title="HASKER's REST API",
      default_version='v1',
      description="API for HASKER site",
      contact=openapi.Contact(email="mail@hasker.site"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


app_name = 'api'

urlpatterns = [
    path('questions', views.get_index, name='index'),
    path('question', views.get_question, name='get_question'),
    path('search', views.get_search, name='search'),
    path('answers', views.get_answers, name='get_answers'),
    path('trending', views.get_trending, name='trending'),
    path('token', obtain_jwt_token, name='obtain_token'),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'.*', views.get_help, name='help'),
]
