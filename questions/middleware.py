from django.utils.deprecation import MiddlewareMixin
from .models import Question
from .views import error_404
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.http import HttpResponse
import json


class TrendingQuestions(MiddlewareMixin):
    """when template rendering, we get trending questions"""

    def process_template_response(self, request, response):

        if not response.context_data:
            return response
        key = make_template_fragment_key('rightbar')
        if cache.get(key):
            return response
        trend_questions, _ = Question.get_questions(True, 1)
        response.context_data["trend_questions"] = trend_questions
        return response


class Error404Exception(MiddlewareMixin):
    """Every error - 404 and our template"""

    def process_exception(self, request, exception):
        if 'rest' in request.path:
            return HttpResponse(json.dumps({'error': 'Not found'}), status=404)
        return error_404(request)
