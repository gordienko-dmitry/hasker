from django.core.mail import EmailMultiAlternatives
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
import hasker.settings as settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
import logging
from django.shortcuts import get_object_or_404


from users.models import UserWithAvatar


logger = logging.getLogger("Questions_Models")


class Tag(models.Model):
    text = models.CharField("Tag", max_length=50, null=False, blank=False, unique=True,
                            error_messages={'unique': "A tag with that text already exists."})

    def __str__(self):
        return self.text


class Question(models.Model):

    title = models.CharField("Title", max_length=200, null=False, blank=False)
    text = models.CharField("Text", max_length=2000, null=False, blank=False)
    pub_date = models.DateTimeField("Publication date", null=False, blank=False, auto_now_add=True)
    tags = models.ManyToManyField(verbose_name="Tags", to=Tag, blank=False)
    author = models.ForeignKey(verbose_name="Author", to=UserWithAvatar, on_delete=models.PROTECT,
                               null=False, blank=False)

    rank = models.IntegerField("Rank", null=False, default=0)

    right_answer = models.IntegerField("Right answer", null=True)

    @staticmethod
    def get_trend_questions():
        batch = settings.QUESTION_BATCH
        return Question.objects.order_by("-rank", "-pub_date").all()[:batch]

    @staticmethod
    def create_question(request):
        with transaction.atomic():

            new_question = Question.objects.create(
                author=request.user,
                title=request.POST.get("title"),
                text=request.POST.get("text")
            )

            # Get all tags from request
            tags = set([tag.strip() for tag in request.POST.get("tag", "").split(",")])

            # Save not existing tags and add all tags to new question
            for tag_text in tags:
                if tag_text:
                    tag, created = Tag.objects.get_or_create(text=tag_text)
                    new_question.tags.add(tag)
            new_question.save()
            return new_question

    @staticmethod
    def get_search(query):
        # Handle tags query
        if query[0][:4] == "tag:":
            tag_text = query[0].split(':')[1]
            if not tag_text:
                tag_text = query[1]
            questions = Question.objects.filter(tags__text=tag_text).order_by("-rank", "-pub_date")

        # Handle simple search query
        else:
            word = query.pop(0)
            questions = Question.objects.filter(models.Q(title__icontains=word) | models.Q(text__icontains=word))
            questions = questions.order_by("-rank", "-pub_date")

            for word in query:
                questions = questions.filter(models.Q(title__icontains=word) | models.Q(text__icontains=word))

        return questions

    def get_url(self):
        return reverse('question', kwargs={"question_id": self.id})

    @staticmethod
    def update_rank(id, up, r=1):
        question = Question.objects.get(id=id)
        if up:
            question.rank += r
        else:
            question.rank -= r
        question.save()
        # cache now useless
        key = make_template_fragment_key('rightbar')
        cache.delete(key)
        return question.rank

    def is_user_vote(self, user):
        try:
            vote = VotesQuestion.objects.get(voter_entity=self, user=user)
        except VotesQuestion.DoesNotExist:
            return ""
        return vote.up_down

    def set_right_answer(self, id_answer, user):
        if user != self.author:
            return
        self.right_answer = id_answer if self.right_answer != id_answer else None
        self.save()
        return

    def get_text_date(self):
        return get_text_date_entities(self)


class Answer(models.Model):
    text = models.CharField("Text", max_length=2000, null=False, blank=False)
    pub_date = models.DateTimeField('Publication date', null=False, blank=False, auto_now_add=True)
    author = models.ForeignKey(verbose_name="Author", to=UserWithAvatar, on_delete=models.PROTECT,
                               null=False, blank=False)
    question = models.ForeignKey(verbose_name="Question", to=Question, on_delete=models.PROTECT,
                                 null=False, blank=False)

    rank = models.IntegerField("Rank", null=False, default=0, db_index=True)

    @staticmethod
    def get_answers(question_id):
        return Answer.objects.filter(question__id=question_id).order_by("-rank", "-pub_date")

    @staticmethod
    def create_answer(request, question):
        new_answer = Answer.objects.create(
            author=request.user,
            question=question,
            text=request.POST.get("answer_text")
        )

        new_answer.save()

        # Notify author of the question with an email
        if settings.EMAIL_HOST_USER:
            subject, from_email, to = "You get an answer to your question", \
                                      'noreply@hasker.com', question.author.email
            text_content = ''
            html_content = settings.EMAIL_TEMPLATE.format(
                question_text=question.question_text,
                link=settings.BASE_URL + question.get_url())

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        return new_answer

    @staticmethod
    def update_rank(id, up, r=1):
        answer = Answer.objects.get(id=id)
        if up:
            answer.rank += r
        else:
            answer.rank -= r
        answer.save()
        return answer.rank

    @staticmethod
    def get_votes(answers, user):
        ids = [answer.id for answer in answers]
        votes = VotesAnswer.objects.filter(voter_entity_id__in=ids)
        result = {}
        for vote in votes:
            result[vote.voter_entity.id] = vote.up_down

        return result

    def get_text_date(self):
        return get_text_date_entities(self)


class VotesQuestion(models.Model):
    """Users, who votes for question"""
    voter_entity = models.ForeignKey(verbose_name="Question", to=Question, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name="User", to=UserWithAvatar, null=False, blank=False, on_delete=models.CASCADE)
    up_down = models.CharField("up or down", null=False, max_length=4)


class VotesAnswer(models.Model):
    """Users, who votes fot answers"""
    voter_entity = models.ForeignKey(verbose_name="Answer", to=Answer, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name="User", to=UserWithAvatar, null=False, blank=False, on_delete=models.CASCADE)
    up_down = models.CharField("up or down", null=False, max_length=4)


def vote_qa(type_entity, id, up, user_id):
    """vote for question or answer"""

    try:
        if type_entity == "q":
            entity = get_object_or_404(Question, id=id)
            vote_obj = VotesQuestion.objects.get_or_create(user_id=user_id, voter_entity_id=id)[0]
        else:
            entity = get_object_or_404(Answer, id=id)
            vote_obj = VotesAnswer.objects.get_or_create(user_id=user_id, voter_entity_id=id)[0]
    except Exception as e:
        logger.exception("false to vote type {}, id {}, up {}, user_id {}, exception {}".
                         format(type_entity, id, up, user_id, e))
        return None, None

    with transaction.atomic():
        up_down = "up" if up else "down"
        vote_obj.up_down = "" if up_down == vote_obj.up_down else up_down
        num = 2 if vote_obj.up_down and up_down != vote_obj.up_down else 1
        new_rank = entity.update_rank(id, up if up_down == vote_obj.up_down else not up, num)
        vote_obj.save()

    return new_rank, vote_obj.up_down


def get_text_date_entities(entity):
    """get text to date info (current data - pub_date)"""

    now_datetime = timezone.now()
    pub_date = entity.pub_date
    if now_datetime.year == pub_date.year or \
            (now_datetime.year - pub_date.year == 1 and
             (now_datetime.month < pub_date.month or
              (now_datetime.month == pub_date.month and now_datetime.day < pub_date.day))):
        delta = timezone.now() - entity.pub_date
        if delta.days < 1:
            return "less than minute ago" if delta.seconds < 60 else "today"

        if delta.days < 365:
            return "{} days ago".format(delta.days)

    return "more than year ago"
