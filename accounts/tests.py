from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SignupViewTestCase(TestCase):
    def setUp(self):
        self.client.logout()

        self.signup_form = {
            'username': 'testuser', 
            'email': 'test@email.com',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }

    def test_url(self):
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_view_creates_user_and_redirects(self):
        response = self.client.post(reverse('signup'), self.signup_form)
        self.assertEqual(response.status_code, 302)
        new_user = get_user_model().objects.last()
        self.assertEqual(new_user.username, self.signup_form['username'])
        self.assertEqual(new_user.email, self.signup_form['email'])
