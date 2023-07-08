from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()
class AuthTestView(APITestCase):
    databases = ["default", ]

    def set_credentials(self, user):
        access_token = AccessToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access_token))
        # self.client.force_login(user=user)

    def setUp(self):
        self.user = User.objects.create_user(
            name="user1",
            email="user1@testing.com",
            password="F4kePaSs0d"
        )
        self.client = APIClient()


    def test_signup(self):
        url = reverse("signup")
        body_request = {
            'name': "Alex",
            'email': "test2@email.com",
            'password': "T3stP@s5Word!"
        }
        users = User.objects.all()
        print("users: ", users)
        response = self.client.post(url, data=body_request)
        body_response = response.json()
        print(body_response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(body_response['ok'], True)
        self.assertTrue(body_response['user'])

        user = get_user_model().objects.get(id=body_response['user'])
        self.assertEqual(user.is_active, False)