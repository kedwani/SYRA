"""Unit tests for the Accounts app."""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from accounts.models import SyraUser, validate_egyptian_national_id

SyraUser = get_user_model()


class ValidateEgyptianNationalIdTest(TestCase):
    """Tests for the validate_egyptian_national_id function."""

    def test_valid_14_digit_national_id(self):
        """Test that a valid 14-digit national ID passes validation."""
        # Should not raise any exception
        validate_egyptian_national_id('12345678901234')

    def test_national_id_with_leading_zeros(self):
        """Test that national ID with leading zeros is valid."""
        validate_egyptian_national_id('00000000000001')

    def test_invalid_national_id_too_short(self):
        """Test that a national ID with less than 14 digits fails."""
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('1234567890123')
        self.assertEqual(context.exception.code, 'invalid_national_id')

    def test_invalid_national_id_too_long(self):
        """Test that a national ID with more than 14 digits fails."""
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('123456789012345')
        self.assertEqual(context.exception.code, 'invalid_national_id')

    def test_invalid_national_id_with_letters(self):
        """Test that a national ID with letters fails."""
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('1234567890123a')
        self.assertEqual(context.exception.code, 'invalid_national_id')

    def test_invalid_national_id_with_special_chars(self):
        """Test that a national ID with special characters fails."""
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('12345678901234!')
        self.assertEqual(context.exception.code, 'invalid_national_id')

    def test_invalid_national_id_empty(self):
        """Test that an empty national ID fails."""
        with self.assertRaises(ValidationError) as context:
            validate_egyptian_national_id('')
        self.assertEqual(context.exception.code, 'invalid_national_id')


class SyraUserModelTest(TestCase):
    """Tests for the SyraUser model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'national_id': '12345678901234',
            'phone_number': '01234567890',
            'password': 'testpassword123'
        }

    def test_create_user_with_valid_data(self):
        """Test creating a user with valid data."""
        user = SyraUser.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.national_id, '12345678901234')
        self.assertEqual(user.phone_number, '01234567890')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = SyraUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            national_id='00000000000001',
            password='adminpass123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_str_representation(self):
        """Test the string representation of the user."""
        user = SyraUser.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser (12345678901234)')

    def test_unique_national_id(self):
        """Test that national_id must be unique."""
        SyraUser.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            SyraUser.objects.create_user(
                username='anotheruser',
                email='another@example.com',
                national_id='12345678901234',  # Same national_id
                password='password123'
            )

    def test_invalid_national_id_on_save(self):
        """Test that invalid national_id raises error on save."""
        user = SyraUser(
            username='testuser2',
            email='test2@example.com',
            national_id='123',  # Invalid - too short
            password='password123'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_optional_phone_number(self):
        """Test that phone_number is optional."""
        user = SyraUser.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            national_id='11111111111111',
            password='password123'
            # phone_number not provided
        )
        self.assertEqual(user.phone_number, '')

    def test_optional_date_of_birth(self):
        """Test that date_of_birth is optional."""
        user = SyraUser.objects.create_user(
            username='testuser4',
            email='test4@example.com',
            national_id='22222222222222',
            password='password123'
            # date_of_birth not provided
        )
        self.assertIsNone(user.date_of_birth)

    def test_user_fields_default_values(self):
        """Test that default field values are set correctly."""
        user = SyraUser.objects.create_user(**self.user_data)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
