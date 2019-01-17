from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .models import Answer, Question, Tag


class NonAuthorizedTest(TestCase):
    """
    One question and one answer
    Let's see, how can non authorized user can use pages:
    - index
    - login
    - signup
    - search
    - question
    - other way (404 error)
    """

    def setUp(self):
        self.user_nobodies = User.objects.create_user(
            username='nobody',
            email='nobody@nowhere.net',
            password='wearethenobodies')

        self.question_who = Question.objects.create(
            title='Who we are?',
            text='We are the nobodies',
            pub_date=timezone.now(),
            author=self.user_nobodies)

        self.answer_who = Answer.objects.create(
            text='Want to be somebodies',
            question=self.question_who,
            pub_date=timezone.now(),
            author=self.user_nobodies)

    def test_index(self):
        response = self.client.get('/')

        self.assertContains(response, 'Sign Up', html=True)
        self.assertContains(response, 'Log In', html=True)
        self.assertContains(response, 'Trending', html=True)
        self.assertContains(response, 'Q: ' + self.question_who.title, html=True)

    def test_login(self):
        response = self.client.get('/login/')

        self.assertContains(response, 'Log In', html=True)
        self.assertContains(response, 'Username', html=True)
        self.assertContains(response, 'Password', html=True)

    def test_signup(self):
        response = self.client.get('/signup/')

        self.assertContains(response, 'SIGN UP', html=True)
        self.assertContains(response, 'e-mail', html=False)
        self.assertContains(response, 'Password', html=False)
        self.assertContains(response, 'Password confirmation', html=False)

    def test_search(self):
        response = self.client.get('/search?query=we')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertContains(response, 'Q: ' + self.question_who.title, html=True)

    def test_question(self):
        response = self.client.get(self.question_who.get_url())
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertContains(response, self.question_who.text, html=True)
        self.assertContains(response, self.answer_who.text, html=True)
        self.assertNotContains(response, 'Your answer', html=True)

    def test_404(self):
        response = self.client.get('/log_up/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'OOPS', status_code=404, html=False)

    def test_ask(self):
        response = self.client.post('/ask/', {'title': 'my own question',
                                              'text': 'Wow, Can I?'})

        self.assertEqual(response.status_code, 404)

    def test_sign_up(self):
        response = self.client.post('/signup/', {'username': 'kurtk',
                                                 'password1': 'smellslikeTS',
                                                 'password2': 'smellslikeTS',
                                                 'email': 'kk@vnirvane.com'})

        self.assertRedirects(response, '/login/')
        self.assertTrue(User.objects.get(username='kurtk'))


class AuthorizedTest(TestCase):
    """
    One question and one answer
    Let's see, how can non authorized user can use pages:
    - index
    - login
    - signup
    - search
    - question
    - other way (404 error)
    """

    def setUp(self):
        self.user_somebody = User.objects.create_user(
            username='somebody',
            email='somebody@somewhere.com',
            password='somecome')

        self.question_think = Question.objects.create(
            title='What do U think?',
            text='What do think today?',
            pub_date=timezone.now(),
            author=self.user_somebody)

        self.answer_think = Answer.objects.create(
            text='Cookies',
            question=self.question_think,
            pub_date=timezone.now(),
            author=self.user_somebody)

        self.client.login(username='somebody', password='somecome')

    def test_index(self):
        response = self.client.get('/')

        self.assertContains(response, 'somebody', html=False)
        self.assertContains(response, 'Log Out', html=True)
        self.assertContains(response, 'Trending', html=True)
        self.assertContains(response, 'Q: ' + self.question_think.title, html=True)

    def test_search(self):
        response = self.client.get('/search?query=think')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertContains(response, 'Q: ' + self.question_think.title, html=True)

    def test_question(self):
        response = self.client.get(self.question_think.get_url())
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertContains(response, self.question_think.text, html=True)
        self.assertContains(response, self.answer_think.text, html=True)
        self.assertContains(response, 'Your answer', html=True)

    def test_404(self):
        response = self.client.get('/log_up/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'OOPS!', status_code=404, html=False)

    def test_ask(self):
        response = self.client.post('/ask', {'title': 'my own question',
                                              'text': 'Wow, Can I?'})

        self.assertTrue(Question.objects.filter(title='my own question').all().count() == 1)

    def test_profile(self):
        response = self.client.get('/profile/')
        self.assertContains(response, 'E-mail', html=True)

        response = self.client.post('/profile/', {'email': 'newborn@new.born'})

        self.assertEqual(User.objects.get(id=self.user_somebody.id).email,
                         'newborn@new.born')

        self.assertRedirects(response, '/profile/')

