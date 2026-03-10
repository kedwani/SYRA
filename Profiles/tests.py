"""
Profiles/tests.py
-----------------
Test suite for the Profiles app.

Covers:
  - MedicalProfile model (creation, public_id uniqueness)
  - Signal auto-creation
  - EmergencyContact (max-2 constraint)
  - Medication CRUD
  - MedicalEvent CRUD
  - Insurance encryption / decryption
  - Profile GET / PUT permissions
  - Insurance endpoint (owner-only)
  - Patient search (by username and UUID)
"""

import io
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    EmergencyContact,
    MedicalEvent,
    MedicalProfile,
    Medication,
    encrypt_file,
    decrypt_file,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def make_user(username, email=None, password="Str0ngPass!"):
    email = email or f"{username}@syra.eg"
    return User.objects.create_user(username=username, email=email, password=password)


def auth_client(client, user):
    """Attach a JWT bearer token to the test client."""
    token = str(RefreshToken.for_user(user).access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class MedicalProfileModelTests(APITestCase):

    def setUp(self):
        self.user = make_user("modeltest")

    def test_signal_creates_profile_on_user_creation(self):
        self.assertTrue(MedicalProfile.objects.filter(user=self.user).exists())

    def test_public_id_is_uuid(self):
        profile = MedicalProfile.objects.get(user=self.user)
        self.assertIsInstance(profile.public_id, uuid.UUID)

    def test_public_id_is_unique_across_profiles(self):
        user2 = make_user("modeltest2")
        p1 = MedicalProfile.objects.get(user=self.user)
        p2 = MedicalProfile.objects.get(user=user2)
        self.assertNotEqual(p1.public_id, p2.public_id)

    def test_str_representation(self):
        profile = MedicalProfile.objects.get(user=self.user)
        self.assertIn("modeltest", str(profile))


class EncryptionTests(APITestCase):
    """Unit tests for the Fernet encryption helpers."""

    def test_encrypt_then_decrypt_returns_original(self):
        # Use a real Fernet key for this test
        from cryptography.fernet import Fernet

        key = Fernet.generate_key().decode()

        with self.settings(SYRA_ENCRYPTION_KEY=key):
            original = b"This is a fake insurance image binary"
            cipher = encrypt_file(original)
            result = decrypt_file(cipher)

        self.assertEqual(result, original)

    def test_encrypted_bytes_differ_from_original(self):
        from cryptography.fernet import Fernet

        key = Fernet.generate_key().decode()
        original = b"Sensitive insurance data"
        with self.settings(SYRA_ENCRYPTION_KEY=key):
            cipher = encrypt_file(original)
        self.assertNotEqual(cipher, original)

    def test_missing_key_raises_runtime_error(self):
        with self.settings(SYRA_ENCRYPTION_KEY=""):
            with self.assertRaises(RuntimeError):
                encrypt_file(b"test")


class EmergencyContactConstraintTests(APITestCase):

    def setUp(self):
        self.user = make_user("contacttest")
        self.profile = MedicalProfile.objects.get(user=self.user)
        auth_client(self.client, self.user)

    def _contact_url(self):
        return reverse("contacts-list", kwargs={"username": self.user.username})

    def test_add_first_contact_succeeds(self):
        res = self.client.post(
            self._contact_url(),
            {
                "name": "Sara Hassan",
                "relationship": "Sister",
                "phone_number": "+201001234567",
                "priority": 1,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_add_second_contact_succeeds(self):
        EmergencyContact.objects.create(
            profile=self.profile, name="A", phone_number="01", priority=1
        )
        res = self.client.post(
            self._contact_url(),
            {
                "name": "Omar Said",
                "relationship": "Father",
                "phone_number": "+201009876543",
                "priority": 2,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_adding_third_contact_is_rejected(self):
        EmergencyContact.objects.create(
            profile=self.profile, name="A", phone_number="01", priority=1
        )
        EmergencyContact.objects.create(
            profile=self.profile, name="B", phone_number="02", priority=2
        )
        res = self.client.post(
            self._contact_url(),
            {
                "name": "Third Person",
                "relationship": "Cousin",
                "phone_number": "+201001111111",
                "priority": 2,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Profile endpoint tests
# ---------------------------------------------------------------------------


class ProfileViewTests(APITestCase):

    def setUp(self):
        self.owner = make_user("owner")
        self.other = make_user("other")
        self.profile = MedicalProfile.objects.get(user=self.owner)

    def _url(self, username=None):
        return reverse(
            "medical-profile", kwargs={"username": username or self.owner.username}
        )

    def test_authenticated_user_can_read_any_profile(self):
        auth_client(self.client, self.other)  # other user reading owner's profile
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_read_profile(self):
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_update_profile(self):
        auth_client(self.client, self.owner)
        res = self.client.put(self._url(), {"blood_type": "O+"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.blood_type, "O+")

    def test_non_owner_cannot_update_profile(self):
        auth_client(self.client, self.other)
        res = self.client.put(self._url(), {"blood_type": "A+"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_insurance_fields_not_in_general_profile_response(self):
        auth_client(self.client, self.owner)
        res = self.client.get(self._url())
        self.assertNotIn("insurance_card_upload", res.data)
        self.assertNotIn("insurance_card_encrypted_path", res.data)
        self.assertNotIn("insurance_card_image", res.data)

    def test_profile_response_includes_required_medical_fields(self):
        auth_client(self.client, self.owner)
        res = self.client.get(self._url())
        for field in (
            "blood_type",
            "gender",
            "chronic_diseases",
            "emergency_contacts",
            "medications",
        ):
            self.assertIn(field, res.data)


# ---------------------------------------------------------------------------
# Insurance endpoint tests
# ---------------------------------------------------------------------------


class InsuranceEndpointTests(APITestCase):

    def setUp(self):
        self.owner = make_user("insowner")
        self.other = make_user("insother")

    def _url(self):
        return reverse("insurance", kwargs={"username": self.owner.username})

    def test_non_owner_cannot_access_insurance(self):
        auth_client(self.client, self.other)
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_insurance(self):
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_read_insurance_endpoint(self):
        auth_client(self.client, self.owner)
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("insurance_company", res.data)

    def test_owner_can_update_insurance_company_name(self):
        auth_client(self.client, self.owner)
        res = self.client.put(
            self._url(), {"insurance_company": "MISR Insurance"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        profile = MedicalProfile.objects.get(user=self.owner)
        self.assertEqual(profile.insurance_company, "MISR Insurance")

    def test_upload_insurance_image_encrypts_on_disk(self):
        from cryptography.fernet import Fernet

        key = Fernet.generate_key().decode()

        with self.settings(SYRA_ENCRYPTION_KEY=key):
            auth_client(self.client, self.owner)
            fake_image = SimpleUploadedFile(
                "card.jpg",
                b"\xff\xd8\xff" + b"\x00" * 100,  # fake JPEG bytes
                content_type="image/jpeg",
            )
            res = self.client.put(
                self._url(),
                {"insurance_company": "TestCo", "insurance_card_upload": fake_image},
                format="multipart",
            )
            self.assertEqual(res.status_code, status.HTTP_200_OK)

        profile = MedicalProfile.objects.get(user=self.owner)
        self.assertTrue(profile.insurance_card_encrypted_path.endswith(".enc"))


# ---------------------------------------------------------------------------
# Medication tests
# ---------------------------------------------------------------------------


class MedicationTests(APITestCase):

    def setUp(self):
        self.user = make_user("meduser")
        self.profile = MedicalProfile.objects.get(user=self.user)
        auth_client(self.client, self.user)

    def _url(self):
        return reverse("medications-list", kwargs={"username": self.user.username})

    def test_list_medications_returns_200(self):
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_add_medication_creates_record(self):
        res = self.client.post(
            self._url(),
            {
                "name": "Metformin",
                "dosage": "500mg twice daily",
                "start_date": "2025-01-01",
                "duration_days": 90,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Medication.objects.filter(profile=self.profile).count(), 1)

    def test_add_medication_without_required_fields_returns_400(self):
        res = self.client.post(self._url(), {"name": "Aspirin"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_medication(self):
        med = Medication.objects.create(
            profile=self.profile, name="Panadol", dosage="1g", start_date="2025-01-01"
        )
        url = reverse(
            "medications-detail", kwargs={"username": self.user.username, "pk": med.pk}
        )
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Medication.objects.filter(pk=med.pk).exists())


# ---------------------------------------------------------------------------
# Medical history tests
# ---------------------------------------------------------------------------


class MedicalHistoryTests(APITestCase):

    def setUp(self):
        self.user = make_user("histuser")
        self.profile = MedicalProfile.objects.get(user=self.user)
        auth_client(self.client, self.user)

    def _url(self):
        return reverse("history-list", kwargs={"username": self.user.username})

    def test_add_accident_event(self):
        res = self.client.post(
            self._url(),
            {
                "event_type": "Accident",
                "description": "Car accident on Cairo ring road",
                "event_date": "2023-05-15",
                "hospital": "Ain Shams Hospital",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicalEvent.objects.filter(profile=self.profile).count(), 1)

    def test_all_event_types_are_accepted(self):
        valid_types = ["Accident", "Fracture", "Bleeding", "Surgery", "Other"]
        for i, etype in enumerate(valid_types):
            res = self.client.post(
                self._url(),
                {
                    "event_type": etype,
                    "description": f"Test {etype}",
                    "event_date": f"2024-0{i+1}-01",
                },
                format="json",
            )
            self.assertEqual(
                res.status_code, status.HTTP_201_CREATED, msg=f"Failed for {etype}"
            )

    def test_invalid_event_type_returns_400(self):
        res = self.client.post(
            self._url(),
            {
                "event_type": "Alien_Attack",
                "description": "Something weird",
                "event_date": "2024-01-01",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Patient search tests
# ---------------------------------------------------------------------------


class PatientSearchTests(APITestCase):

    def setUp(self):
        self.searcher = make_user("searcher")
        self.target = make_user("targetpatient")
        self.profile = MedicalProfile.objects.get(user=self.target)
        auth_client(self.client, self.searcher)

    def _url(self, q):
        return f"{reverse('patient-search')}?q={q}"

    def test_search_by_username_returns_profile(self):
        res = self.client.get(self._url("targetpatient"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], "targetpatient")

    def test_search_by_uuid_returns_profile(self):
        res = self.client.get(self._url(str(self.profile.public_id)))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["public_id"], str(self.profile.public_id))

    def test_search_nonexistent_patient_returns_404(self):
        res = self.client.get(self._url("nobody_here"))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_search_query_returns_400(self):
        res = self.client.get(f"{reverse('patient-search')}?q=")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_without_auth_returns_401(self):
        self.client.credentials()  # clear token
        res = self.client.get(self._url("targetpatient"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_result_does_not_expose_insurance_data(self):
        res = self.client.get(self._url("targetpatient"))
        self.assertNotIn("insurance_card_image", res.data)
        self.assertNotIn("insurance_card_encrypted_path", res.data)
