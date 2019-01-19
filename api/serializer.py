from rest_framework import serializers


class QuestionSerializer(serializers.Serializer):
    """
    Question serializer with all fields
    """
    id = serializers.IntegerField()
    title = serializers.CharField(required=True, allow_blank=False,
                                  max_length=100)
    author = serializers.CharField(required=True, allow_blank=False,
                                   max_length=100)
    pub_date = serializers.DateTimeField(format="%x %X")
    tags = serializers.ManyRelatedField(child_relation=serializers.CharField())

    text = serializers.CharField(required=True, allow_blank=False,
                                 max_length=2000)

    number_of_answers = serializers.SerializerMethodField()
    rank = serializers.IntegerField()

    def get_number_of_answers(self, obj):
        """
        :return: number of answers for number_of_answer field
        """
        return obj.answer_set.count()


class QuestionTrendingSerializer(QuestionSerializer):
    """
    Only id, title and rank
    """
    text = None
    tags = None
    author = None
    number_of_answers = None
    pub_date = None


class QuestionWithoutTextSerializer(QuestionSerializer):
    """
    Question without text
    """
    text = None


class AnswerSerializer(serializers.Serializer):
    """
    Answer serializer
    """

    author = serializers.CharField(required=True, allow_blank=False,
                                   max_length=100)
    rank = serializers.IntegerField()

    text = serializers.CharField(required=True, allow_blank=False,
                                 max_length=2000)
