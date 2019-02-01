from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone


class NonAuthorizedTest(TestCase):
    """
    One question and one answer
    Let's see, how can non authorized user can use pages:
    - login
    - signup
    - other way (404 error)
    """

    def setUp(self):
        self.user_nobodies = User.objects.create_user(
            username='nobody',
            email='nobody@nowhere.net',
            password='wearethenobodies')

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

    def test_404(self):
        response = self.client.get('/log_up/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'OOPS', status_code=404, html=False)

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
    - login
    - signup
    - other way (404 error)
    """

    def setUp(self):
        self.user_somebody = User.objects.create_user(
            username='somebody',
            email='somebody@somewhere.com',
            password='somecome')

        self.client.login(username='somebody', password='somecome')

    def test_404(self):
        response = self.client.get('/log_up/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'OOPS!', status_code=404, html=False)

    def test_profile(self):
        response = self.client.get('/profile/')
        self.assertContains(response, 'E-mail', html=True)

        response = self.client.post('/profile/', {'email': 'newborn@new.born'})

        self.assertEqual(User.objects.get(id=self.user_somebody.id).email,
                         'newborn@new.born')

        self.assertRedirects(response, '/profile/')
