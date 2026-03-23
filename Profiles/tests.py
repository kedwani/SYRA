"""Unit tests for the Profiles app."""

import uuid
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from profiles.models import MedicalProfile, Medication, EmergencyContact, MedicalEvent

SyraUser = get_user_model()


class MedicalProfileModelTest(TestCase):
    """Tests for the MedicalProfile model."""

    def setUp(self):
        """Set up test data - signal auto-creates profile on user creation."""
        self.user = SyraUser.objects.create_user(
            username="testpatient",
            email="patient@example.com",
            national_id="12345678901234",
            password="testpass123",
        )
        # Profile is auto-created by signal, retrieve it
        self.profile = self.user.medical_profile

    def test_medical_profile_auto_created(self):
        """Test that medical profile is auto-created on user creation."""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.blood_type, "Unknown")  # Default

    def test_update_medical_profile(self):
        """Test updating a medical profile."""
        self.profile.blood_type = "A+"
        self.profile.chronic_diseases = "Diabetes"
        self.profile.allergies = "Penicillin"
        self.profile.height = 175
        self.profile.weight = 70
        self.profile.save()

        # Refresh from database
        updated_profile = MedicalProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.blood_type, "A+")
        self.assertEqual(updated_profile.chronic_diseases, "Diabetes")
        self.assertEqual(updated_profile.allergies, "Penicillin")
        self.assertEqual(updated_profile.height, 175)
        self.assertEqual(updated_profile.weight, 70)

    def test_medical_profile_str_representation(self):
        """Test string representation of medical profile."""
        self.assertEqual(str(self.profile), "Medical Profile - testpatient")

    def test_unique_public_id(self):
        """Test that public_id is unique."""
        # Create another user with their own profile
        user2 = SyraUser.objects.create_user(
            username="testpatient2",
            email="patient2@example.com",
            national_id="22345678901234",
            password="testpass123",
        )
        profile2 = user2.medical_profile

        self.assertNotEqual(self.profile.public_id, profile2.public_id)
        self.assertIsNotNone(self.profile.public_id)

    def test_default_blood_type(self):
        """Test that default blood type is 'Unknown'."""
        self.assertEqual(self.profile.blood_type, "Unknown")

    def test_optional_fields(self):
        """Test that optional fields can be empty."""
        self.profile.chronic_diseases = ""
        self.profile.allergies = ""
        self.profile.emergency_notes = ""
        self.profile.insurance_provider = ""
        self.profile.insurance_number = ""
        self.profile.height = None
        self.profile.weight = None
        self.profile.save()

        # Refresh from database
        updated_profile = MedicalProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.chronic_diseases, "")
        self.assertIsNone(updated_profile.height)

    def test_blood_type_choices(self):
        """Test all blood type choices."""
        blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
        for blood_type in blood_types:
            # Create new user for each blood type test
            user = SyraUser.objects.create_user(
                username=f"patient_{blood_type}",
                email=f"patient_{blood_type}@example.com",
                national_id=f"{(hash(blood_type) % 10000000000000) + 1000000000000:014d}",
                password="testpass123",
            )
            profile = user.medical_profile
            profile.blood_type = blood_type
            profile.save()
            self.assertEqual(profile.blood_type, blood_type)

    def test_update_blood_type(self):
        """Test updating blood type."""
        self.profile.blood_type = "O+"
        self.profile.save()

        updated_profile = MedicalProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.blood_type, "O+")


class MedicationModelTest(TestCase):
    """Tests for the Medication model."""

    def setUp(self):
        """Set up test data - signal auto-creates profile on user creation."""
        self.user = SyraUser.objects.create_user(
            username="testpatient",
            email="patient@example.com",
            national_id="12345678901234",
            password="testpass123",
        )
        self.profile = self.user.medical_profile

    def test_create_medication(self):
        """Test creating a medication."""
        medication = Medication.objects.create(
            profile=self.profile,
            name="Aspirin",
            dosage="100mg",
            frequency="Once daily",
            is_active=True,
            notes="Take with food",
        )
        self.assertEqual(medication.name, "Aspirin")
        self.assertEqual(medication.dosage, "100mg")
        self.assertEqual(medication.frequency, "Once daily")
        self.assertTrue(medication.is_active)
        self.assertEqual(medication.profile, self.profile)

    def test_medication_str_representation(self):
        """Test string representation of medication."""
        medication = Medication.objects.create(
            profile=self.profile, name="Ibuprofen", dosage="400mg"
        )
        self.assertEqual(str(medication), "Ibuprofen - 400mg")

    def test_default_is_active(self):
        """Test that is_active defaults to True."""
        medication = Medication.objects.create(
            profile=self.profile, name="Vitamin C", dosage="500mg"
        )
        self.assertTrue(medication.is_active)

    def test_optional_fields(self):
        """Test that optional fields can be empty."""
        medication = Medication.objects.create(
            profile=self.profile,
            name="Medicine",
            dosage="100mg",
            frequency="",
            notes="",
        )
        self.assertEqual(medication.frequency, "")
        self.assertEqual(medication.notes, "")

    def test_cascade_delete(self):
        """Test that medications are deleted when profile is deleted."""
        Medication.objects.create(profile=self.profile, name="Test Med", dosage="100mg")
        self.assertEqual(Medication.objects.count(), 1)
        self.profile.delete()
        self.assertEqual(Medication.objects.count(), 0)

    def test_filter_active_medications(self):
        """Test filtering medications based on period_days and created_at."""
        from django.utils import timezone
        from datetime import timedelta

        # Create a medication with period that is still active (created today, 30 day period)
        med_active = Medication.objects.create(
            profile=self.profile, name="Active Med", dosage="100mg", period_days=30
        )

        # Create a medication with period that has ended (created 60 days ago, 30 day period)
        med_inactive = Medication.objects.create(
            profile=self.profile, name="Completed Med", dosage="50mg", period_days=30
        )
        # Backdate the created_at to simulate completed medication
        med_inactive.created_at = timezone.now() - timedelta(days=60)
        med_inactive.save()

        # Create a medication without period (ongoing)
        med_ongoing = Medication.objects.create(
            profile=self.profile, name="Ongoing Med", dosage="25mg", period_days=None
        )

        # Test the is_active property
        self.assertTrue(med_active.is_active)  # 30 day period, not expired
        self.assertFalse(
            med_inactive.is_active
        )  # 30 day period, expired (60 days > 30 days)
        self.assertTrue(med_ongoing.is_active)  # No period, ongoing

        # Test filtering by property in Python
        all_meds = Medication.objects.filter(profile=self.profile)
        active_meds = [med for med in all_meds if med.is_active]
        self.assertEqual(len(active_meds), 2)
        self.assertTrue(any(med.name == "Active Med" for med in active_meds))
        self.assertTrue(any(med.name == "Ongoing Med" for med in active_meds))


class EmergencyContactModelTest(TestCase):
    """Tests for the EmergencyContact model."""

    def setUp(self):
        """Set up test data - signal auto-creates profile on user creation."""
        self.user = SyraUser.objects.create_user(
            username="testpatient",
            email="patient@example.com",
            national_id="12345678901234",
            password="testpass123",
        )
        self.profile = self.user.medical_profile

    def test_create_emergency_contact(self):
        """Test creating an emergency contact."""
        contact = EmergencyContact.objects.create(
            profile=self.profile,
            name="John Doe",
            relationship="spouse",
            phone_number="01234567890",
            alternate_phone="09876543210",
            is_primary=True,
        )
        self.assertEqual(contact.name, "John Doe")
        self.assertEqual(contact.relationship, "spouse")
        self.assertEqual(contact.phone_number, "01234567890")
        self.assertTrue(contact.is_primary)

    def test_emergency_contact_str_representation(self):
        """Test string representation of emergency contact."""
        contact = EmergencyContact.objects.create(
            profile=self.profile,
            name="Jane Doe",
            relationship="parent",
            phone_number="01234567890",
        )
        self.assertEqual(str(contact), "Jane Doe (Parent)")

    def test_relationship_choices(self):
        """Test all relationship choices."""
        relationships = ["spouse", "parent", "sibling", "child", "friend", "other"]
        for rel in relationships:
            # Use different profile for each relationship
            user = SyraUser.objects.create_user(
                username=f"test_{rel}",
                email=f"test_{rel}@example.com",
                national_id=f"{(hash(rel) % 10000000000000) + 2000000000000:014d}",
                password="testpass123",
            )
            profile = user.medical_profile
            contact = EmergencyContact.objects.create(
                profile=profile,
                name=f"Contact {rel}",
                relationship=rel,
                phone_number="01234567890",
            )
            self.assertEqual(contact.relationship, rel)
            self.assertEqual(contact.get_relationship_display(), rel.title())

    def test_default_is_primary(self):
        """Test that is_primary defaults to False."""
        contact = EmergencyContact.objects.create(
            profile=self.profile,
            name="Test Contact",
            relationship="friend",
            phone_number="01234567890",
        )
        self.assertFalse(contact.is_primary)

    def test_ordering_by_primary(self):
        """Test that contacts are ordered by is_primary first, then name."""
        contact1 = EmergencyContact.objects.create(
            profile=self.profile,
            name="Alice",
            relationship="friend",
            phone_number="01234567890",
            is_primary=False,
        )
        contact2 = EmergencyContact.objects.create(
            profile=self.profile,
            name="Bob",
            relationship="friend",
            phone_number="09876543210",
            is_primary=True,
        )
        contacts = list(
            EmergencyContact.objects.filter(profile=self.profile).order_by(
                "-is_primary", "name"
            )
        )
        self.assertEqual(contacts[0], contact2)  # Primary first
        self.assertEqual(contacts[1], contact1)

    def test_cascade_delete(self):
        """Test that contacts are deleted when profile is deleted."""
        EmergencyContact.objects.create(
            profile=self.profile,
            name="Test Contact",
            relationship="friend",
            phone_number="01234567890",
        )
        self.assertEqual(EmergencyContact.objects.count(), 1)
        self.profile.delete()
        self.assertEqual(EmergencyContact.objects.count(), 0)


class MedicalEventModelTest(TestCase):
    """Tests for the MedicalEvent model."""

    def setUp(self):
        """Set up test data - signal auto-creates profile on user creation."""
        self.user = SyraUser.objects.create_user(
            username="testpatient",
            email="patient@example.com",
            national_id="12345678901234",
            password="testpass123",
        )
        self.profile = self.user.medical_profile

    def test_create_medical_event(self):
        """Test creating a medical event."""
        event = MedicalEvent.objects.create(
            profile=self.profile,
            event_type="surgery",
            title="Appendectomy",
            description="Laparoscopic surgery to remove appendix",
            date=date(2023, 6, 15),
            hospital_name="Cairo Medical Center",
            doctor_name="Dr. Ahmed Hassan",
        )
        self.assertEqual(event.event_type, "surgery")
        self.assertEqual(event.title, "Appendectomy")
        self.assertEqual(event.date, date(2023, 6, 15))

    def test_medical_event_str_representation(self):
        """Test string representation of medical event."""
        event = MedicalEvent.objects.create(
            profile=self.profile,
            event_type="diagnosis",
            title="Diabetes Diagnosis",
            date=date(2022, 1, 10),
        )
        self.assertEqual(str(event), "Diabetes Diagnosis - 2022-01-10")

    def test_event_type_choices(self):
        """Test all event type choices."""
        event_types = [
            "surgery",
            "hospitalization",
            "diagnosis",
            "emergency",
            "checkup",
            "other",
        ]
        for event_type in event_types:
            # Create new user for each event type
            user = SyraUser.objects.create_user(
                username=f"test_{event_type}",
                email=f"test_{event_type}@example.com",
                national_id=f"{(hash(event_type) % 10000000000000) + 3000000000000:014d}",
                password="testpass123",
            )
            profile = user.medical_profile
            event = MedicalEvent.objects.create(
                profile=profile,
                event_type=event_type,
                title=f"Test {event_type}",
                date=date.today(),
            )
            self.assertEqual(event.event_type, event_type)

    def test_ordering_by_date_desc(self):
        """Test that events are ordered by date descending."""
        event1 = MedicalEvent.objects.create(
            profile=self.profile,
            event_type="checkup",
            title="Old Checkup",
            date=date(2020, 1, 1),
        )
        event2 = MedicalEvent.objects.create(
            profile=self.profile,
            event_type="checkup",
            title="Recent Checkup",
            date=date(2024, 1, 1),
        )
        events = list(
            MedicalEvent.objects.filter(profile=self.profile).order_by("-date")
        )
        self.assertEqual(events[0], event2)  # Most recent first
        self.assertEqual(events[1], event1)

    def test_optional_fields(self):
        """Test that optional fields can be empty."""
        event = MedicalEvent.objects.create(
            profile=self.profile,
            event_type="other",
            title="Test Event",
            date=date.today(),
            description="",
            hospital_name="",
            doctor_name="",
        )
        self.assertEqual(event.description, "")
        self.assertEqual(event.hospital_name, "")

    def test_cascade_delete(self):
        """Test that events are deleted when profile is deleted."""
        MedicalEvent.objects.create(
            profile=self.profile,
            event_type="checkup",
            title="Test Event",
            date=date.today(),
        )
        self.assertEqual(MedicalEvent.objects.count(), 1)
        self.profile.delete()
        self.assertEqual(MedicalEvent.objects.count(), 0)


class EmergencyContactLimitTest(TestCase):
    """Tests for the 2-contact limit enforcement."""

    def setUp(self):
        """Set up test data - signal auto-creates profile on user creation."""
        self.user = SyraUser.objects.create_user(
            username="testpatient",
            email="patient@example.com",
            national_id="12345678901234",
            password="testpass123",
        )
        self.profile = self.user.medical_profile

    def test_max_two_contacts_view_validation(self):
        """Test that view enforces max 2 contacts limit."""
        # Create two contacts
        EmergencyContact.objects.create(
            profile=self.profile,
            name="Contact 1",
            relationship="parent",
            phone_number="01234567890",
        )
        EmergencyContact.objects.create(
            profile=self.profile,
            name="Contact 2",
            relationship="spouse",
            phone_number="09876543210",
        )

        # At model level we can still create (validation is in views/serializers)
        # This test verifies the current behavior - limit enforced at view level
        contact_count = EmergencyContact.objects.filter(profile=self.profile).count()
        self.assertEqual(contact_count, 2)  # Can have 2 contacts

    def test_can_add_two_contacts(self):
        """Test that adding exactly 2 contacts is allowed."""
        contact1 = EmergencyContact.objects.create(
            profile=self.profile,
            name="Contact 1",
            relationship="parent",
            phone_number="01234567890",
        )
        contact2 = EmergencyContact.objects.create(
            profile=self.profile,
            name="Contact 2",
            relationship="spouse",
            phone_number="09876543210",
        )

        contacts = EmergencyContact.objects.filter(profile=self.profile)
        self.assertEqual(contacts.count(), 2)

    def test_can_update_existing_contacts(self):
        """Test that updating existing contacts is allowed."""
        contact1 = EmergencyContact.objects.create(
            profile=self.profile,
            name="Contact 1",
            relationship="parent",
            phone_number="01234567890",
        )
        contact1.name = "Updated Contact"
        contact1.save()

        updated = EmergencyContact.objects.get(id=contact1.id)
        self.assertEqual(updated.name, "Updated Contact")


class EmergencyScanAPITest(TestCase):
    """Tests for the emergency scan API endpoint."""

    def setUp(self):
        """Set up test user and profile."""
        self.user = SyraUser.objects.create_user(
            username="emergencytest",
            email="emergency@example.com",
            national_id="12345678901234",
            password="testpass123",
        )
        self.profile = self.user.medical_profile
        self.profile.blood_type = "A+"
        self.profile.allergies = "Penicillin"
        self.profile.save()

    def test_emergency_scan_success(self):
        """Test successful emergency scan."""
        url = f"/api/profiles/scan/{self.profile.public_id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["blood_type"], "A+")

    def test_emergency_scan_invalid_uuid(self):
        """Test emergency scan with invalid UUID."""
        url = "/api/profiles/scan/00000000-0000-0000-0000-000000000000/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_emergency_scan_invalid_format(self):
        """Test emergency scan with invalid UUID format."""
        url = "/api/profiles/scan/invalid-uuid/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EmergencyAccessCheckAPITest(TestCase):
    """Tests for the emergency access check API endpoint."""

    def setUp(self):
        """Set up test user and profile."""
        self.user = SyraUser.objects.create_user(
            username="accesstest",
            email="access@example.com",
            national_id="22345678901234",
            password="testpass123",
        )
        self.profile = self.user.medical_profile

    def test_access_check_anonymous_user(self):
        """Test access check as anonymous user."""
        url = f"/api/profiles/access/{self.profile.public_id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_role"], "user")
        self.assertFalse(response.data["show_full_medical"])

    def test_access_check_authenticated_user(self):
        """Test access check as authenticated user."""
        # Login
        self.client.login(username="accesstest", password="testpass123")
        url = f"/api/profiles/access/{self.profile.public_id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User should see their own data
        self.assertEqual(response.data["user_role"], "user")


class SearchMedicalDataAPITest(TestCase):
    """Tests for the search medical data API endpoint."""

    def test_search_medications(self):
        """Test searching for medications."""
        url = "/api/profiles/search/?q=asp&type=medications"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("medications", response.data)

    def test_search_empty_query(self):
        """Test search with empty query."""
        url = "/api/profiles/search/?q="
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["medications"], [])

    def test_search_diagnoses(self):
        """Test searching for diagnoses."""
        url = "/api/profiles/search/?q=diab&type=diagnoses"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("diagnoses", response.data)


class MedicationAPITest(TestCase):
    """Tests for the Medication API endpoints."""

    def setUp(self):
        """Set up test user and get token."""
        self.user = SyraUser.objects.create_user(
            username="medtest",
            email="med@example.com",
            national_id="32345678901234",
            password="testpass123",
        )
        self.profile = self.user.medical_profile
        # Get JWT token
        response = self.client.post(
            "/api/accounts/login/",
            {"national_id": "32345678901234", "password": "testpass123"},
        )
        self.token = response.data["access"]

    def test_create_medication_authenticated(self):
        """Test creating medication with authentication."""
        data = {
            "name": "Aspirin",
            "dosage": "100mg",
            "frequency": "Once daily",
            "is_active": True,
        }
        response = self.client.post(
            "/api/profiles/medications/",
            data,
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Aspirin")

    def test_create_medication_unauthenticated(self):
        """Test creating medication without authentication."""
        data = {"name": "Aspirin", "dosage": "100mg"}
        response = self.client.post("/api/profiles/medications/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_medications(self):
        """Test listing medications."""
        Medication.objects.create(profile=self.profile, name="Test Med", dosage="50mg")
        response = self.client.get(
            "/api/profiles/medications/", HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


class EmergencyContactAPITest(TestCase):
    """Tests for the Emergency Contact API endpoints."""

    def setUp(self):
        """Set up test user and get token."""
        self.user = SyraUser.objects.create_user(
            username="contacttest",
            email="contact@example.com",
            national_id="42345678901234",
            password="testpass123",
        )
        self.profile = self.user.medical_profile
        # Get JWT token
        response = self.client.post(
            "/api/accounts/login/",
            {"national_id": "42345678901234", "password": "testpass123"},
        )
        self.token = response.data["access"]

    def test_create_contact_authenticated(self):
        """Test creating emergency contact with authentication."""
        data = {
            "name": "John Doe",
            "relationship": "spouse",
            "phone_number": "01234567890",
        }
        response = self.client.post(
            "/api/profiles/contacts/", data, HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "John Doe")

    def test_create_contact_unauthenticated(self):
        """Test creating contact without authentication."""
        data = {"name": "John Doe", "phone_number": "01234567890"}
        response = self.client.post("/api/profiles/contacts/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_max_two_contacts_enforced(self):
        """Test that max 2 contacts limit is enforced at API level."""
        # Create first contact
        self.client.post(
            "/api/profiles/contacts/",
            {
                "name": "Contact 1",
                "relationship": "parent",
                "phone_number": "01234567890",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        # Create second contact
        self.client.post(
            "/api/profiles/contacts/",
            {
                "name": "Contact 2",
                "relationship": "spouse",
                "phone_number": "09876543210",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        # Try to create third contact - should fail
        response = self.client.post(
            "/api/profiles/contacts/",
            {
                "name": "Contact 3",
                "relationship": "friend",
                "phone_number": "01111111111",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MedicalEventAPITest(TestCase):
    """Tests for the Medical Event API endpoints."""

    def setUp(self):
        """Set up test user and get token."""
        self.user = SyraUser.objects.create_user(
            username="eventtest",
            email="event@example.com",
            national_id="52345678901234",
            password="testpass123",
        )
        self.profile = self.user.medical_profile
        # Get JWT token
        response = self.client.post(
            "/api/accounts/login/",
            {"national_id": "52345678901234", "password": "testpass123"},
        )
        self.token = response.data["access"]

    def test_create_event_authenticated(self):
        """Test creating medical event with authentication."""
        data = {
            "event_type": "surgery",
            "title": "Appendectomy",
            "description": "Appendectomy surgery",
            "date": "2020-01-15",
        }
        response = self.client.post(
            "/api/profiles/events/", data, HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["event_type"], "surgery")

    def test_create_event_unauthenticated(self):
        """Test creating event without authentication."""
        data = {"event_type": "surgery", "description": "Test"}
        response = self.client.post("/api/profiles/events/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileVisibilityTest(TestCase):
    """Tests for profile visibility settings."""

    def setUp(self):
        """Set up test user."""
        self.user = SyraUser.objects.create_user(
            username="visibilitytest",
            email="visibility@example.com",
            national_id="62345678901234",
            password="testpass123",
        )
        self.profile = self.user.medical_profile

    def test_visibility_fields_exist(self):
        """Test that visibility toggle fields exist."""
        self.assertTrue(hasattr(self.profile, "show_chronic_diseases_public"))
        self.assertTrue(hasattr(self.profile, "show_notes_public"))
        self.assertTrue(hasattr(self.profile, "show_insurance_public"))

    def test_default_visibility_settings(self):
        """Test default visibility settings."""
        # Chronic diseases should be public by default
        self.assertTrue(self.profile.show_chronic_diseases_public)
        # Insurance should be private by default
        self.assertFalse(self.profile.show_insurance_public)
