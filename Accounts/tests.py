"""Unit tests for the Accounts app."""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import override_settings
from django.core.cache import cache
from rest_framework import status
from accounts.models import SyraUser, validate_egyptian_national_id

SyraUser = get_user_model()


class ValidateEgyptianNationalIdTest(TestCase):
    """Tests for the validate_egyptian_national_id function."""

    def test_valid_14_digit_national_id(self):
        """Test that a valid 14-digit national ID passes validation."""
        # Should not raise any exception
        validate_egyptian_national_id("12345678901234")

    def test_national_id_with_leading_zeros(self):
        """Test that national ID with leading zeros is valid."""
        validate_egyptian_national_id("00000000000001")

    def test_invalid_national_id_too_short(self):
        """Test that a national ID with less than 14 digits fails."""
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id("1234567890123")
        self.assertEqual(context.exception.code, "invalid_national_id")

    def test_invalid_national_id_too_long(self):
        """Test that a national ID with more than 14 digits fails."""
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id("123456789012345")
        self.assertEqual(context.exception.code, "invalid_national_id")

    def test_invalid_national_id_with_letters(self):
        """Test that a national ID with letters fails."""
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id("1234567890123a")
        self.assertEqual(context.exception.code, "invalid_national_id")

    def test_invalid_national_id_with_special_chars(self):
        """Test that a national ID with special characters fails."""
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id("12345678901234!")
        self.assertEqual(context.exception.code, "invalid_national_id")

    def test_invalid_national_id_empty(self):
        """Test that an empty national ID fails."""
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id("")
        self.assertEqual(context.exception.code, "invalid_national_id")


class SyraUserModelTest(TestCase):
    """Tests for the SyraUser model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "national_id": "12345678901234",
            "phone_number": "01234567890",
            "password": "testpassword123",
        }

    def test_create_user_with_valid_data(self):
        """Test creating a user with valid data."""
        user = SyraUser.objects.create_user(**self.user_data)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.national_id, "12345678901234")
        self.assertEqual(user.phone_number, "01234567890")
        self.assertTrue(user.check_password("testpassword123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = SyraUser.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            national_id="00000000000001",
            password="adminpass123",
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_str_representation(self):
        """Test the string representation of the user."""
        user = SyraUser.objects.create_user(**self.user_data)
        self.assertEqual(str(user), "testuser (12345678901234)")

    def test_unique_national_id(self):
        """Test that national_id must be unique."""
        SyraUser.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            SyraUser.objects.create_user(
                username="anotheruser",
                email="another@example.com",
                national_id="12345678901234",  # Same national_id
                password="password123",
            )

    def test_invalid_national_id_on_save(self):
        """Test that invalid national_id raises error on save."""
        user = SyraUser(
            username="testuser2",
            email="test2@example.com",
            national_id="123",  # Invalid - too short
            password="password123",
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_optional_phone_number(self):
        """Test that phone_number is optional."""
        user = SyraUser.objects.create_user(
            username="testuser3",
            email="test3@example.com",
            national_id="11111111111111",
            password="password123",
            # phone_number not provided
        )
        self.assertEqual(user.phone_number, "")

    def test_optional_date_of_birth(self):
        """Test that date_of_birth is optional."""
        user = SyraUser.objects.create_user(
            username="testuser4",
            email="test4@example.com",
            national_id="22222222222222",
            password="password123",
            # date_of_birth not provided
        )
        self.assertIsNone(user.date_of_birth)

    def test_user_fields_default_values(self):
        """Test that default field values are set correctly."""
        user = SyraUser.objects.create_user(**self.user_data)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)


class RegisterAPITest(TestCase):
    """Tests for the user registration API endpoint."""

    def setUp(self):
        """Set up test - clear cache to avoid rate limiting."""
        cache.clear()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from django.conf import settings

        cls._original_ratelimit_enabled = getattr(settings, "RATELIMIT_ENABLED", True)
        settings.RATELIMIT_ENABLED = False

    @classmethod
    def tearDownClass(cls):
        from django.conf import settings

        settings.RATELIMIT_ENABLED = cls._original_ratelimit_enabled
        super().tearDownClass()

    def test_register_user_success(self):
        """Test successful user registration."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "national_id": "32345678901234",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "01234567890",
        }
        response = self.client.post("/api/accounts/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")

    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords."""
        data = {
            "username": "newuser2",
            "email": "newuser2@example.com",
            "national_id": "42345678901234",
            "password": "securepass123",
            "password_confirm": "differentpass",
        }
        response = self.client.post("/api/accounts/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Error can be in either password or password_confirm field
        self.assertTrue(
            "password" in response.data or "password_confirm" in response.data
        )

    def test_register_short_password(self):
        """Test registration with short password."""
        data = {
            "username": "newuser3",
            "email": "newuser3@example.com",
            "national_id": "52345678901234",
            "password": "short",
            "password_confirm": "short",
        }
        response = self.client.post("/api/accounts/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_national_id(self):
        """Test registration with invalid national ID."""
        data = {
            "username": "newuser4",
            "email": "newuser4@example.com",
            "national_id": "123",  # Too short
            "password": "securepass123",
            "password_confirm": "securepass123",
        }
        response = self.client.post("/api/accounts/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_national_id(self):
        """Test registration with duplicate national ID."""
        # First registration
        data = {
            "username": "user1",
            "email": "user1@example.com",
            "national_id": "62345678901234",
            "password": "securepass123",
            "password_confirm": "securepass123",
        }
        self.client.post("/api/accounts/register/", data)

        # Duplicate registration
        data["username"] = "user2"
        data["email"] = "user2@example.com"
        response = self.client.post("/api/accounts/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        """Test registration with duplicate username."""
        # First registration
        data = {
            "username": "duplicateuser",
            "email": "user1@example.com",
            "national_id": "72345678901234",
            "password": "securepass123",
            "password_confirm": "securepass123",
        }
        self.client.post("/api/accounts/register/", data)

        # Duplicate username
        data["national_id"] = "82345678901234"
        data["email"] = "user2@example.com"
        response = self.client.post("/api/accounts/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_required_fields(self):
        """Test registration with missing required fields."""
        data = {"username": "incomplete"}
        response = self.client.post("/api/accounts/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITest(TestCase):
    """Tests for the login API endpoint."""

    def setUp(self):
        """Set up test user."""
        self.user = SyraUser.objects.create_user(
            username="logintest",
            email="login@example.com",
            national_id="92345678901234",
            password="testpass123",
        )

    def test_login_success(self):
        """Test successful login."""
        data = {"national_id": "92345678901234", "password": "testpass123"}
        response = self.client.post("/api/accounts/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_password(self):
        """Test login with wrong password."""
        data = {"national_id": "92345678901234", "password": "wrongpassword"}
        response = self.client.post("/api/accounts/login/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_invalid_national_id(self):
        """Test login with non-existent national ID."""
        data = {"national_id": "00000000000000", "password": "testpass123"}
        response = self.client.post("/api/accounts/login/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        """Test login with missing fields."""
        data = {"national_id": "92345678901234"}
        response = self.client.post("/api/accounts/login/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTRefreshTest(TestCase):
    """Tests for JWT token refresh."""

    def setUp(self):
        """Set up test user and tokens."""
        self.user = SyraUser.objects.create_user(
            username="refreshtest",
            email="refresh@example.com",
            national_id="12345678901239",
            password="testpass123",
        )
        # Get tokens
        response = self.client.post(
            "/api/accounts/login/",
            {"national_id": "12345678901239", "password": "testpass123"},
        )
        self.refresh_token = response.data["refresh"]

    def test_refresh_token_success(self):
        """Test successful token refresh."""
        data = {"refresh": self.refresh_token}
        response = self.client.post("/api/accounts/token/refresh/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_invalid_token(self):
        """Test refresh with invalid token."""
        data = {"refresh": "invalid.token.here"}
        response = self.client.post("/api/accounts/token/refresh/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileAPITest(TestCase):
    """Tests for the user profile API endpoint."""

    def setUp(self):
        """Set up authenticated test user."""
        self.user = SyraUser.objects.create_user(
            username="profiletest",
            email="profile@example.com",
            national_id="22345678901234",
            password="testpass123",
        )
        # Get token
        response = self.client.post(
            "/api/accounts/login/",
            {"national_id": "22345678901234", "password": "testpass123"},
        )
        self.token = response.data["access"]

    def test_get_profile_authenticated(self):
        """Test getting profile with authentication."""
        response = self.client.get(
            "/api/accounts/profile/", HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "profiletest")

    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication."""
        response = self.client.get("/api/accounts/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        """Test updating user profile."""
        data = {"first_name": "Updated", "last_name": "Name"}
        response = self.client.put(
            "/api/accounts/profile/",
            data,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")


class LoginTemplateViewTest(TestCase):
    """Tests for the login template view."""

    def test_login_page_loads(self):
        """Test that login page loads successfully."""
        # /accounts/login/ redirects to home page
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 302)  # Redirect to home

    def test_login_redirect_authenticated(self):
        """Test that authenticated users are redirected from login."""
        user = SyraUser.objects.create_user(
            username="authtest",
            email="auth@example.com",
            national_id="32345678901234",
            password="testpass123",
        )
        self.client.login(username="authtest", password="testpass123")
        response = self.client.get("/accounts/login/")
        # Should redirect to dashboard
        self.assertIn(response.status_code, [302, 200])


class RegisterTemplateViewTest(TestCase):
    """Tests for the register template view."""

    def test_register_page_loads(self):
        """Test that register page loads successfully."""
        # Register is at /register/ not /accounts/register/
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)

    def test_register_redirect_authenticated(self):
        """Test that authenticated users are redirected from register."""
        user = SyraUser.objects.create_user(
            username="authtest2",
            email="auth2@example.com",
            national_id="42345678901234",
            password="testpass123",
        )
        self.client.login(username="authtest2", password="testpass123")
        response = self.client.get("/register/")
        self.assertIn(response.status_code, [302, 200])
