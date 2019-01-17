from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.mail import EmailMultiAlternatives
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
import hasker.settings as settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key


EMAIL_TEMPLATE = "<p>Hey, we get new answer on your question:</p> " \
                 "<p><b>{question_text}</p></b><br>" \
                 "<p>You can go by this link and read an answer:<p>" \
                 "<p><a href='{link}'>read answer</a></p><br>" \
                 "<p>---</p><br>" \
                 "<p>This is automatic message, please do ot answer</p>"


class UserWithAvatar(models.Model):
    """add avatar to user"""
    user = models.OneToOneField(to=User,
                                on_delete=models.CASCADE,
                                null=False, blank=False)
    avatar = models.ImageField(upload_to="static/img", null=True)

    @staticmethod
    def get_user(user_id):
        """get or create user"""
        try:
            return UserWithAvatar.objects.get(user_id=user_id)
        except UserWithAvatar.DoesNotExist:
            return UserWithAvatar.objects.create(user_id=user_id)

    def update_profile(self, email, avatar):
        """change user e-mail or avatar"""
        with transaction.atomic():
            if self.user.email != email:
                self.user.email = email
                self.user.save()

            if avatar:
                self.avatar = avatar
                self.save()


class Tag(models.Model):
    text = models.CharField("tag", max_length=50, null=False, blank=False, unique=True,
                            error_messages={'unique': "A tag with that text already exists."})

    def __str__(self):
        return self.text


class Question(models.Model):

    title = models.CharField(max_length=200, null=False, blank=False)
    text = models.CharField(max_length=2000, null=False, blank=False)
    pub_date = models.DateTimeField('date published', null=False, blank=False)
    tags = models.ManyToManyField(to=Tag, blank=False)
    author = models.ForeignKey(to=User, on_delete=models.PROTECT,
                               null=False, blank=False)

    rank = models.IntegerField(null=False, default=0)

    right_answer = models.IntegerField(null=True)

    @staticmethod
    def get_questions(hot=False, page=1, batch=None):

        if not batch:
            batch = settings.QUESTION_BATCH

        if hot:
            result = Question.objects.order_by("-rank", "-pub_date").all()
        else:
            result = Question.objects.order_by("-pub_date", "-rank").all()

        paginator = Paginator(result, batch)
        result = paginator.get_page(page)
        return result, paginator.num_pages

    @staticmethod
    def create_question(request):
        with transaction.atomic():

            new_question = Question.objects.create(
                author=request.user,
                title=request.POST.get("title"),
                text=request.POST.get("text"),
                pub_date=timezone.now()
            )

            # Get all tags from request
            tags = set([tag.strip() for tag in request.POST.get("tag", "").split(",")])

            # Save not existing tags and add all tags to new question
            for tag_text in tags:
                if tag_text:
                    try:
                        tag = Tag.objects.get(text=tag_text)
                    except Tag.DoesNotExist:
                        tag = Tag.objects.create(text=tag_text)
                        tag.save()
                    new_question.tags.add(tag)

            new_question.save()

            return new_question

    @staticmethod
    def get_search(query, page, batch=None):
        if not batch:
            batch = settings.SEARCH_BATCH

        # Handle tags query
        if query[0][:4] == "tag:":
            tag_text = query[0].split(':')[1]
            if not tag_text:
                tag_text = query[1]
            questions = Question.objects.all()
            try:
                tag = Tag.objects.get(text=tag_text).id
                questions = questions.filter(tags=tag).order_by("-rank", "-pub_date")
            except Tag.DoesNotExist:
                questions = None

        # Handle simple search query
        else:
            word = query.pop(0)
            questions = Question.objects.filter(models.Q(title__icontains=word) | models.Q(text__icontains=word))
            questions = questions.order_by("-rank", "-pub_date")

            for word in query:
                questions = questions.filter(models.Q(title__icontains=word) | models.Q(text__icontains=word))

        paginator = Paginator(questions, batch)
        questions = paginator.get_page(page)
        return questions, paginator.num_pages

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
            return False
        if self.right_answer == id_answer:
            self.right_answer = None
        else:
            self.right_answer = id_answer
        self.save()
        return True

    def get_text_date(self):
        return get_text_date_entities(self)


class Answer(models.Model):
    text = models.CharField(max_length=2000, null=False, blank=False)
    pub_date = models.DateTimeField('date published', null=False, blank=False)
    author = models.ForeignKey(to=User, on_delete=models.PROTECT,
                               null=False, blank=False)
    question = models.ForeignKey(to=Question, on_delete=models.PROTECT,
                                 null=False, blank=False)

    rank = models.IntegerField(null=False, default=0, db_index=True)

    @staticmethod
    def get_answers(question, page, batch=None):
        if not batch:
            batch = settings.ANSWERS_BATCH

        result = Answer.objects.filter(question=question).order_by("-rank", "-pub_date")
        paginator = Paginator(result, batch)
        result = paginator.get_page(page)
        return result, paginator.num_pages

    @staticmethod
    def create_answer(request, question):
        new_answer = Answer.objects.create(
            author=request.user,
            question=question,
            text=request.POST.get("answer_text"),
            pub_date=timezone.now()
        )

        new_answer.save()

        # Notify author of the question with an email
        if settings.EMAIL_HOST_USER:
            subject, from_email, to = "You get an answer to your question", \
                                      'noreply@hasker.com', question.author.email
            text_content = ''
            html_content = EMAIL_TEMPLATE.format(
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
    voter_entity = models.ForeignKey(to=Question, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, null=False, blank=False, on_delete=models.CASCADE)
    up_down = models.CharField("up or down", null=False, max_length=4)


class VotesAnswer(models.Model):
    voter_entity = models.ForeignKey(to=Answer, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, null=False, blank=False, on_delete=models.CASCADE)
    up_down = models.CharField("up or down", null=False, max_length=4)


def vote_qa(type_entity, id, up, user_id):
    """vote for question or answer"""

    try:
        if type_entity == "q":
            entity = Question.objects.get(id=id)
            vote_class = VotesQuestion
            vote_obj = VotesQuestion.objects.get(user_id=user_id, voter_entity_id=id)
        else:
            entity = Answer.objects.get(id=id)
            vote_class = VotesAnswer
            vote_obj = VotesAnswer.objects.get(user_id=user_id, voter_entity_id=id)
    except (VotesQuestion.DoesNotExist, VotesAnswer.DoesNotExist):
        vote_obj = None
    except Exception:
        return None, None

    with transaction.atomic():
        if vote_obj:
            if up:
                if vote_obj.up_down == "up":
                    vote_obj.up_down = ""
                    new_rank = entity.update_rank(id, False)
                elif vote_obj.up_down == "down":
                    vote_obj.up_down = "up"
                    new_rank = entity.update_rank(id, up, 2)
                else:
                    vote_obj.up_down = "up"
                    new_rank = entity.update_rank(id, up)
            else:
                if vote_obj.up_down == "down":
                    vote_obj.up_down = ""
                    new_rank = entity.update_rank(id, True)
                elif vote_obj.up_down == "up":
                    vote_obj.up_down = "down"
                    new_rank = entity.update_rank(id, up, 2)
                else:
                    vote_obj.up_down = "down"
                    new_rank = entity.update_rank(id, up)

            vote_obj.save()

        else:
            up_down = "up" if up else "down"
            vote_obj = vote_class.objects.create(voter_entity=entity, user_id=user_id, up_down=up_down)
            new_rank = entity.update_rank(id, up)

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
        if delta.days < 1 and delta.seconds < 60:
            return "less than minute ago"
        if delta.days < 365:
            return "{} days ago".format(delta.days)

    return "more than year ago"
