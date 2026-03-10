"""Unit tests for the Profiles app."""
import uuid
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from profiles.models import (
    MedicalProfile, Medication, EmergencyContact, MedicalEvent
)

SyraUser = get_user_model()


class MedicalProfileModelTest(TestCase):
    """Tests for the MedicalProfile model."""

    def setUp(self):
        """Set up test data."""
        self.user = SyraUser.objects.create_user(
            username='testpatient',
            email='patient@example.com',
            national_id='12345678901234',
            password='testpass123'
        )

    def test_create_medical_profile(self):
        """Test creating a medical profile."""
        profile = MedicalProfile.objects.create(
            user=self.user,
            blood_type='A+',
            chronic_diseases='Diabetes, Hypertension',
            allergies='Penicillin',
            emergency_notes='Allergic to penicillin',
            height=175,
            weight=70
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.blood_type, 'A+')
        self.assertEqual(profile.chronic_diseases, 'Diabetes, Hypertension')
        self.assertEqual(profile.allergies, 'Penicillin')
        self.assertEqual(profile.height, 175)
        self.assertEqual(profile.weight, 70)
        self.assertIsNotNone(profile.public_id)

    def test_medical_profile_str_representation(self):
        """Test string representation of medical profile."""
        profile = MedicalProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), 'Medical Profile - testpatient')

    def test_unique_public_id(self):
        """Test that public_id is unique."""
        profile1 = MedicalProfile.objects.create(user=self.user)
        # Create another user with their own profile
        user2 = SyraUser.objects.create_user(
            username='testpatient2',
            email='patient2@example.com',
            national_id='22345678901234',
            password='testpass123'
        )
        profile2 = MedicalProfile.objects.create(user=user2)
        self.assertNotEqual(profile1.public_id, profile2.public_id)

    def test_default_blood_type(self):
        """Test that default blood type is 'Unknown'."""
        profile = MedicalProfile.objects.create(user=self.user)
        self.assertEqual(profile.blood_type, 'Unknown')

    def test_optional_fields(self):
        """Test that optional fields can be empty."""
        profile = MedicalProfile.objects.create(
            user=self.user,
            chronic_diseases='',
            allergies='',
            emergency_notes='',
            insurance_provider='',
            insurance_number='',
            height=None,
            weight=None
        )
        self.assertEqual(profile.chronic_diseases, '')
        self.assertIsNone(profile.height)

    def test_blood_type_choices(self):
        """Test all blood type choices."""
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown']
        for blood_type in blood_types:
            user = SyraUser.objects.create_user(
                username=f'patient_{blood_type}',
                email=f'patient_{blood_type}@example.com',
                national_id=f'{blood_type}45678901234'.replace('+', '1').replace('-', '1'),
                password='testpass123'
            )
            profile = MedicalProfile.objects.create(user=user, blood_type=blood_type)
            self.assertEqual(profile.blood_type, blood_type)


class MedicationModelTest(TestCase):
    """Tests for the Medication model."""

    def setUp(self):
        """Set up test data."""
        self.user = SyraUser.objects.create_user(
            username='testpatient',
            email='patient@example.com',
            national_id='12345678901234',
            password='testpass123'
        )
        self.profile = MedicalProfile.objects.create(user=self.user)

    def test_create_medication(self):
        """Test creating a medication."""
        medication = Medication.objects.create(
            profile=self.profile,
            name='Aspirin',
            dosage='100mg',
            frequency='Once daily',
            is_active=True,
            notes='Take with food'
        )
        self.assertEqual(medication.name, 'Aspirin')
        self.assertEqual(medication.dosage, '100mg')
        self.assertEqual(medication.frequency, 'Once daily')
        self.assertTrue(medication.is_active)
        self.assertEqual(medication.profile, self.profile)

    def test_medication_str_representation(self):
        """Test string representation of medication."""
        medication = Medication.objects.create(
            profile=self.profile,
            name='Ibuprofen',
            dosage='400mg'
        )
        self.assertEqual(str(medication), 'Ibuprofen - 400mg')

    def test_default_is_active(self):
        """Test that is_active defaults to True."""
        medication = Medication.objects.create(
            profile=self.profile,
            name='Vitamin C',
            dosage='500mg'
        )
        self.assertTrue(medication.is_active)

    def test_optional_fields(self):
        """Test that optional fields can be empty."""
        medication = Medication.objects.create(
            profile=self.profile,
            name='Medicine',
            dosage='100mg',
            frequency='',
            notes=''
        )
        self.assertEqual(medication.frequency, '')
        self.assertEqual(medication.notes, '')

    def test_cascade_delete(self):
        """Test that medications are deleted when profile is deleted."""
        Medication.objects.create(
            profile=self.profile,
            name='Test Med',
            dosage='100mg'
        )
        self.assertEqual(Medication.objects.count(), 1)
        self.profile.delete()
        self.assertEqual(Medication.objects.count(), 0)


class EmergencyContactModelTest(TestCase):
    """Tests for the EmergencyContact model."""

    def setUp(self):
        """Set up test data."""
        self.user = SyraUser.objects.create_user(
            username='testpatient',
            email='patient@example.com',
            national_id='12345678901234',
            password='testpass123'
        )
        self.profile = MedicalProfile.objects.create(user=self.user)

    def test_create_emergency_contact(self):
        """Test creating an emergency contact."""
        contact = EmergencyContact.objects.create(
            profile=self.profile,
            name='John Doe',
            relationship='spouse',
            phone_number='01234567890',
            alternate_phone='09876543210',
            is_primary=True
        )
        self.assertEqual(contact.name, 'John Doe')
        self.assertEqual(contact.relationship, 'spouse')
        self.assertEqual(contact.phone_number, '01234567890')
        self.assertTrue(contact.is_primary)

    def test_emergency_contact_str_representation(self):
        """Test string representation of emergency contact."""
        contact = EmergencyContact.objects.create(
            profile=self.profile,
            name='Jane Doe',
            relationship='parent',
            phone_number='01234567890'
        )
        self.assertEqual(str(contact), 'Jane Doe (Parent)')

    def test_relationship_choices(self):
        """Test all relationship choices."""
        relationships = ['spouse', 'parent', 'sibling', 'child', 'friend', 'other']
        for rel in relationships:
            contact = EmergencyContact.objects.create(
                profile=self.profile,
                name=f'Contact {rel}',
                relationship=rel,
                phone_number='01234567890'
            )
            self.assertEqual(contact.relationship, rel)
            self.assertEqual(contact.get_relationship_display(), rel.title())

    def test_default_is_primary(self):
        """Test that is_primary defaults to False."""
        contact = EmergencyContact.objects.create(
            profile=self.profile,
            name='Test Contact',
            relationship='friend',
            phone_number='01234567890'
        )
        self.assertFalse(contact.is_primary)

    def test_ordering_by_primary(self):
        """Test that contacts are ordered by is_primary first, then name."""
        contact1 = EmergencyContact.objects.create(
            profile=self.profile,
            name='Alice',
            relationship='friend',
            phone_number='01234567890',
            is_primary=False
        )
        contact2 = EmergencyContact.objects.create(
            profile=self.profile,
            name='Bob',
            relationship='friend',
            phone_number='09876543210',
            is_primary=True
        )
        contacts = list(EmergencyContact.objects.all())
        self.assertEqual(contacts[0], contact2)  # Primary first
        self.assertEqual(contacts[1], contact1)

    def test_cascade_delete(self):
        """Test that contacts are deleted when profile is deleted."""
        EmergencyContact.objects.create(
            profile=self.profile,
            name='Test Contact',
            relationship='friend',
            phone_number='01234567890'
        )
        self.assertEqual(EmergencyContact.objects.count(), 1)
        self.profile.delete()
        self.assertEqual(EmergencyContact.objects.count(), 0)


class MedicalEventModelTest(TestCase):
    """Tests for the MedicalEvent model."""

    def setUp(self):
        """Set up test data."""
        self.user = SyraUser.objects.create_user(
            username='testpatient',
            email='patient@example.com',
            national_id='12345678901234',
            password='testpass123'
        )
        self.profile = MedicalProfile.objects.create(user=self.user)

    def test_create_medical_event(self):
        """Test creating a medical event."""
        event = MedicalEvent.objects.create(
            profile=self.profile,
            event_type='surgery',
            title='Appendectomy',
            description='Laparoscopic surgery to remove appendix',
            date=date(2023, 6, 15),
            hospital_name='Cairo Medical Center',
            doctor_name='Dr. Ahmed Hassan'
        )
        self.assertEqual(event.event_type, 'surgery')
        self.assertEqual(event.title, 'Appendectomy')
        self.assertEqual(event.date, date(2023, 6, 15))

    def test_medical_event_str_representation(self):
        """Test string representation of medical event."""
        event = MedicalEvent.objects.create(
            profile=self.profile,
            event_type='diagnosis',
            title='Diabetes Diagnosis',
            date=date(2022, 1, 10)
        )
        self.assertEqual(str(event), 'Diabetes Diagnosis - 2022-01-10')

    def test_event_type_choices(self):
        """Test all event type choices."""
        event_types = ['surgery', 'hospitalization', 'diagnosis', 'emergency', 'checkup', 'other']
        for event_type in event_types:
            event = MedicalEvent.objects.create(
                profile=self.profile,
                event_type=event_type,
                title=f'Test {event_type}',
                date=date.today()
            )
            self.assertEqual(event.event_type, event_type)

    def test_ordering_by_date_desc(self):
        """Test that events are ordered by date descending."""
        event1 = MedicalEvent.objects.create(
            profile=self.profile,
            event_type='checkup',
            title='Old Checkup',
            date=date(2020, 1, 1)
        )
        event2 = MedicalEvent.objects.create(
            profile=self.profile,
            event_type='checkup',
            title='Recent Checkup',
            date=date(2024, 1, 1)
        )
        events = list(MedicalEvent.objects.all())
        self.assertEqual(events[0], event2)  # Most recent first

    def test_optional_fields(self):
        """Test that optional fields can be empty."""
        event = MedicalEvent.objects.create(
            profile=self.profile,
            event_type='other',
            title='Test Event',
            date=date.today(),
            description='',
            hospital_name='',
            doctor_name=''
        )
        self.assertEqual(event.description, '')
        self.assertEqual(event.hospital_name, '')

    def test_cascade_delete(self):
        """Test that events are deleted when profile is deleted."""
        MedicalEvent.objects.create(
            profile=self.profile,
            event_type='checkup',
            title='Test Event',
            date=date.today()
        )
        self.assertEqual(MedicalEvent.objects.count(), 1)
        self.profile.delete()
        self.assertEqual(MedicalEvent.objects.count(), 0)


class EmergencyContactLimitTest(TestCase):
    """Tests for the 2-contact limit enforcement."""

    def setUp(self):
        """Set up test data."""
        self.user = SyraUser.objects.create_user(
            username='testpatient',
            email='patient@example.com',
            national_id='12345678901234',
            password='testpass123'
        )
        self.profile = MedicalProfile.objects.create(user=self.user)

    def test_max_two_contacts_validation(self):
        """Test that adding more than 2 contacts raises validation error."""
        # Create two contacts
        EmergencyContact.objects.create(
            profile=self.profile,
            name='Contact 1',
            relationship='parent',
            phone_number='01234567890'
        )
        EmergencyContact.objects.create(
            profile=self.profile,
            name='Contact 2',
            relationship='spouse',
            phone_number='09876543210'
        )
        
        # Try to add a third contact - should fail
        contact3 = EmergencyContact(
            profile=self.profile,
            name='Contact 3',
            relationship='friend',
            phone_number='01111111111'
        )
        with self.assertRaises(ValidationError):
            contact3.full_clean()
