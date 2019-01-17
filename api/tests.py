import json

from http import HTTPStatus

from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.utils import timezone

from questions.models import Question, Tag


class HaskerApiTest(APITestCase):

    def setUp(self):

        self.user1 = User.objects.create_user(
            username='StarLord',
            email='sl@galaxy.mail',
            password='galaxyindanger1')

        self.user2 = User.objects.create_user(
            username='mayflower',
            email='may21@flower.com',
            password='password')

        self.tag = Tag.objects.create(text='one')

        self.question1 = Question.objects.create(
            title='Simple title',
            text='Blah blah blah one two three',
            pub_date=timezone.now(),
            author=self.user1)

        self.question1.tags.add(self.tag)
        self.question1.save()

        self.question2 = Question.objects.create(
            title='Intriguing title',
            text='four five six',
            pub_date=timezone.now(),
            author=self.user2)

        self.client.login(username=self.user2.username, password='password')

        self.client.post(self.question2.get_url(), {'answer_text': 'I got an answer'})

        response = self.client.post('/rest/token',
                                    {'username': self.user1.username,
                                     'password': 'galaxyindanger1'})

        self.token = response.data["token"]

        self.client.post('/vote', {'id': self.question1.id, 'up': 'true', 'entity': 'q'})

    def test_answer(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))

        response = self.client.get(
            '/rest/answers?question_id={}'.format(self.question2.id)
        )

        json_response = json.loads(response._container[0].decode('utf-8'))["answers"]
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["text"], "I got an answer")

    def test_bad_auth(self):
        # Answers page
        response = self.client.get(
            '/rest/answers?question_id={}'.format(self.question2.id))
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        # Question page
        response = self.client.get(
            '/rest/question?question_id={}'.format(self.question1.id)
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        # Search
        response = self.client.get('/rest/search?query=title')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_batch(self):
        response = self.client.get('/rest/questions?batch=1')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], self.question1.id)

    def test_questions_by_date(self):
        response = self.client.get('/rest/questions?order=date')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0]["id"], self.question2.id)

    def test_questions_by_rating(self):
        response = self.client.get('/rest/questions?order=rating')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0]["id"], self.question1.id)

    def test_page(self):
        response = self.client.get('/rest/questions?batch=1&page=2')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], self.question2.id)

    def test_question_info(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))

        response = self.client.get(
            '/rest/question?question_id={}'.format(self.question1.id)
        )

        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(json_response["text"], self.question1.text)
        self.assertEqual(json_response["rank"], 1)

    def test_search_by_tag(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))
        response = self.client.get('/rest/search?query=tag:one')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], self.question1.id)

    def test_search_by_word(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))
        response = self.client.get('/rest/search?query=title')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0]["id"], self.question1.id)

    def test_trending(self):
        response = self.client.get('/rest/trending')

        json_response = json.loads(response.content.decode('utf-8'))["trending_questions"]
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0]["id"], self.question1.id)
