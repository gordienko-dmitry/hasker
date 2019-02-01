from drf_yasg import openapi

param_order = openapi.Parameter('order_by', openapi.IN_QUERY, description="ordering (rating or date)",
                                type=openapi.TYPE_STRING)
param_batch = openapi.Parameter('batch', openapi.IN_QUERY, description="number of questions on page",
                                type=openapi.TYPE_INTEGER)
param_page = openapi.Parameter('page', openapi.IN_QUERY, description="page number",
                               type=openapi.TYPE_INTEGER)
param_count = openapi.Parameter('count', openapi.IN_QUERY, description="count questions in answer",
                                type=openapi.TYPE_INTEGER)
param_query = openapi.Parameter('query', openapi.IN_QUERY, description="text of query for searching",
                                type=openapi.TYPE_STRING)
param_question_id = openapi.Parameter('question_id', openapi.IN_QUERY, description="id for question",
                                      type=openapi.TYPE_INTEGER)
