import json

from http import HTTPStatus
from django.http import HttpResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .serializer import AnswerSerializer, QuestionSerializer, \
    QuestionWithoutTextSerializer, QuestionTrendingSerializer

from questions.models import Answer, Question

from drf_yasg.utils import swagger_auto_schema

from .swagger_params import *


@swagger_auto_schema(method='get', manual_parameters=[param_order, param_batch, param_page])
@api_view(['GET'])
def get_index(request):
    """Get list of questions"""

    order_by = request.GET.get('order', 'rating')
    batch = request.GET.get('batch', 10)
    page = request.GET.get('page', 1)

    if order_by not in ["date", "rating"]:
        order_by = "rating"

    questions, count_pages = Question.get_questions(order_by == "rating", page, batch)
    questions_serialized = QuestionWithoutTextSerializer(questions, many=True)

    return HttpResponse(
        json.dumps({
            'page': page,
            'max_pages': count_pages,
            'order by': order_by,
            'questions': questions_serialized.data,
        }))


@swagger_auto_schema(method='get', manual_parameters=[param_count])
@api_view(['GET'])
def get_trending(request):
    """Get some (or ten) trending questions"""

    count = request.GET.get('count', 10)

    questions, _ = Question.get_questions(True, 1, count)
    serialized_questions = QuestionTrendingSerializer(questions, many=True)
    return HttpResponse(json.dumps({"trending_questions": serialized_questions.data, "count": count}))


@swagger_auto_schema(method='get', manual_parameters=[param_query, param_page, param_batch])
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_search(request):
    """Get result of search"""

    query = request.GET.get("query")
    page = request.GET.get("page", 1)
    batch = request.GET.get("batch", 10)
    search_query = query.split()

    if not search_query:
        return HttpResponse(content=json.dumps({"error": "empty search query"}),
                            status=HTTPStatus.BAD_REQUEST)

    questions, count_pages = Question.get_search(search_query, page, batch)
    questions_serialized = QuestionWithoutTextSerializer(questions, many=True)

    return HttpResponse(json.dumps({'page': page,
                                    'max_pages': count_pages,
                                    'questions': questions_serialized.data,
                                    }))


@swagger_auto_schema(method='get', manual_parameters=[param_question_id])
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_question(request):
    """Get info of one question"""

    question_id = request.GET.get('question_id')
    if not question_id:
        return HttpResponse(content=json.dumps({"error": "no question id in request"}),
                            status=HTTPStatus.BAD_REQUEST)

    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return HttpResponse(content=json.dumps({"error": "no question with this question id"}),
                            status=HTTPStatus.NOT_FOUND)

    questions_serialized = QuestionSerializer(question)
    return HttpResponse(json.dumps(questions_serialized.data))


@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def get_help(_):
    """Get all allowed methods"""

    return HttpResponse(json.dumps({"Allowed methods": ["rest/questions",
                                                        "rest/question",
                                                        "rest/answers",
                                                        "rest/search",
                                                        "rest/trending",
                                                        "rest/token"]}))


@swagger_auto_schema(method='get', manual_parameters=[param_question_id, param_page, param_batch])
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_answers(request):
    """Get answers of one question"""

    question_id = request.GET.get('question_id')
    if not question_id:
        return HttpResponse(content=json.dumps({"error": "no id in request"}),
                            status=HTTPStatus.BAD_REQUEST)
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return HttpResponse(content=json.dumps({"error": "no question with this question id"}),
                            status=HTTPStatus.NOT_FOUND)

    page = request.GET.get("page", 1)
    batch = request.GET.get("batch", 10)

    answers, count_pages = Answer.get_answers(question, page, batch)
    serialized_answers = AnswerSerializer(answers, many=True)
    return HttpResponse(json.dumps({"question_id": question_id,
                                    "question_title": question.title,
                                    "question_text": question.text,
                                    "page": page,
                                    "count_pages": count_pages,
                                    "answers": serialized_answers.data}, indent=4))
