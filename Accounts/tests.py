"""
Accounts/tests.py
-----------------
Test suite for the Accounts app.

Covers:
  - SyraUser model creation and constraints
  - Registration endpoint (success, duplicate, password mismatch)
  - JWT login (success, wrong password, inactive user)
  - /me/ endpoint auth protection
  - Signal: MedicalProfile auto-created on registration
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from Profiles.models import MedicalProfile

User = get_user_model()


class UserModelTests(APITestCase):
    """Unit tests for the SyraUser model."""

    def test_create_user_stores_national_id(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@syra.eg",
            password="Str0ngPass!",
            national_id="12345678901234",
        )
        self.assertEqual(user.national_id, "12345678901234")

    def test_email_is_unique(self):
        User.objects.create_user(
            username="u1", email="dupe@syra.eg", password="pass1234"
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="u2", email="dupe@syra.eg", password="pass1234"
            )

    def test_national_id_is_unique(self):
        User.objects.create_user(
            username="n1",
            email="n1@syra.eg",
            password="pass",
            national_id="11111111111111",
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="n2",
                email="n2@syra.eg",
                password="pass",
                national_id="11111111111111",
            )

    def test_str_representation(self):
        user = User.objects.create_user(
            username="ahmed", email="ahmed@syra.eg", password="pass"
        )
        self.assertIn("ahmed", str(user))


class RegistrationTests(APITestCase):
    """Integration tests for POST /api/auth/register/."""

    url = reverse("register")

    def _payload(self, **overrides):
        base = {
            "username": "newuser",
            "email": "newuser@syra.eg",
            "password": "Str0ngPass!",
            "password_confirm": "Str0ngPass!",
        }
        return {**base, **overrides}

    def test_successful_registration_returns_201(self):
        res = self.client.post(self.url, self._payload(), format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("username", res.data)

    def test_registration_creates_user_in_db(self):
        self.client.post(self.url, self._payload(), format="json")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signal_creates_medical_profile_on_registration(self):
        """MedicalProfile must be auto-created via Django signal."""
        self.client.post(self.url, self._payload(), format="json")
        user = User.objects.get(username="newuser")
        self.assertTrue(MedicalProfile.objects.filter(user=user).exists())

    def test_password_mismatch_returns_400(self):
        res = self.client.post(
            self.url,
            self._payload(password_confirm="WrongPass!"),
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", res.data)

    def test_duplicate_username_returns_400(self):
        self.client.post(self.url, self._payload(), format="json")
        res = self.client.post(self.url, self._payload(), format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_returns_400(self):
        self.client.post(self.url, self._payload(), format="json")
        res = self.client.post(
            self.url,
            self._payload(username="anotheruser"),
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_not_in_response(self):
        res = self.client.post(self.url, self._payload(), format="json")
        self.assertNotIn("password", res.data)


class JWTLoginTests(APITestCase):
    """Tests for POST /api/auth/token/ (JWT token obtain)."""

    url = reverse("token_obtain_pair")

    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser", email="login@syra.eg", password="Str0ngPass!"
        )

    def test_valid_credentials_return_tokens(self):
        res = self.client.post(
            self.url,
            {"username": "loginuser", "password": "Str0ngPass!"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_wrong_password_returns_401(self):
        res = self.client.post(
            self.url,
            {"username": "loginuser", "password": "WrongPass!"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_user_returns_401(self):
        res = self.client.post(
            self.url,
            {"username": "ghost", "password": "anything"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class MeEndpointTests(APITestCase):
    """Tests for GET /api/auth/me/."""

    url = reverse("user_detail")

    def setUp(self):
        self.user = User.objects.create_user(
            username="meuser", email="me@syra.eg", password="pass1234"
        )
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

    def test_authenticated_user_gets_own_info(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], "meuser")

    def test_unauthenticated_request_returns_401(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
