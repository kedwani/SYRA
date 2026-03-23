"""Template views for the Profiles app - Patient dashboard."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
import logging

logger = logging.getLogger(__name__)

from .models import MedicalProfile, Medication, EmergencyContact, MedicalEvent
from .serializers import (
    MedicalProfileSerializer,
    MedicationSerializer,
    EmergencyContactSerializer,
    MedicalEventSerializer,
)
from .emergency_utils import decode_emergency_data
from .views import get_user_role


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@login_required
def dashboard_view(request):
    """Patient dashboard - view and manage medical profile."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        profile = None

    # Calculate pending count using annotation to avoid N+1 queries
    pending_count = 0
    if profile:
        from django.db.models import Count, Q

        result = (
            MedicalProfile.objects.filter(id=profile.id)
            .annotate(
                pending_meds=Count(
                    "medications", filter=Q(medications__pending_approval=True)
                ),
                pending_contacts=Count(
                    "emergency_contacts",
                    filter=Q(emergency_contacts__pending_approval=True),
                ),
                pending_events=Count(
                    "medical_events", filter=Q(medical_events__pending_approval=True)
                ),
            )
            .first()
        )
        if result:
            pending_count = (
                result.pending_meds + result.pending_contacts + result.pending_events
            )

    # Get featured products from store (limit to 4)
    from store.models import SyraBand

    featured_products = SyraBand.objects.filter(
        is_active=True, is_featured=True, stock_quantity__gt=0
    )[:4]

    # Get latest products (limit to 4)
    latest_products = SyraBand.objects.filter(
        is_active=True, stock_quantity__gt=0
    ).order_by("-created_at")[:4]

    context = {
        "profile": profile,
        "profile_serializer": (
            MedicalProfileSerializer(profile).data if profile else None
        ),
        "pending_count": pending_count,
        "hide_navigation": True,
        "featured_products": featured_products,
        "latest_products": latest_products,
    }
    return render(request, "profiles/dashboard.html", context)


@login_required
def profile_edit_view(request):
    """Edit medical profile."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        profile = MedicalProfile.objects.create(user=request.user)

    if request.method == "POST":
        # Create mutable copy of POST data
        post_data = request.POST.copy()

        # Fix: Explicitly set visibility fields to False if not present in POST
        # This is necessary because unchecked checkboxes don't submit any value
        visibility_fields = [
            "show_blood_type_public",
            "show_allergies_public",
            "show_medications_public",
            "show_contacts_public",
            "show_physical_public",
            "show_history_public",
            "show_chronic_diseases_public",
            "show_notes_public",
            "show_insurance_public",
        ]
        for field in visibility_fields:
            if field in post_data and post_data[field] in ["on", "true", "1", "yes"]:
                post_data[field] = True
            else:
                post_data[field] = False

        # Debug: Log visibility fields
        logger.info(f"POST data visibility fields:")
        for key in post_data:
            if "show_" in key:
                logger.info(f"  {key}: {post_data.get(key)}")

        serializer = MedicalProfileSerializer(profile, data=post_data, partial=True)

        if serializer.is_valid():
            # Debug: Log validated data
            logger.info(f"Validated serializer data for visibility:")
            for key in serializer.validated_data:
                if "show_" in key:
                    logger.info(f"  {key}: {serializer.validated_data.get(key)}")

            # Handle file upload separately
            if "insurance_image" in request.FILES:
                from django.core.files.base import ContentFile

                uploaded_file = request.FILES["insurance_image"]
                # Read file content into memory first to avoid closed file handle issues
                file_content = uploaded_file.read()
                # Create a new ContentFile with the content - this avoids InMemoryUploadedFile issues
                profile.insurance_image.save(
                    uploaded_file.name, ContentFile(file_content), save=False
                )
                # Now save the profile - encryption will happen in the save() method
                profile.save()
            else:
                serializer.save()

            # Debug: Log saved profile visibility values
            profile.refresh_from_db()
            logger.info(f"Saved profile visibility values:")
            for field in [
                "show_blood_type_public",
                "show_allergies_public",
                "show_medications_public",
                "show_contacts_public",
                "show_physical_public",
                "show_history_public",
                "show_chronic_diseases_public",
                "show_notes_public",
                "show_insurance_public",
            ]:
                logger.info(f"  {field}: {getattr(profile, field)}")

            messages.success(request, "Profile updated successfully.")
            return redirect("dashboard")
    else:
        serializer = MedicalProfileSerializer(profile)

    # Get related data for display
    medications = profile.medications.all()
    contacts = profile.emergency_contacts.all()
    medical_events = profile.medical_events.all()

    # Calculate BMI
    calculated_bmi = None
    bmi_category = None
    if profile.height and profile.weight:
        height_m = profile.height / 100
        calculated_bmi = round(profile.weight / (height_m**2), 1)
        if calculated_bmi < 18.5:
            bmi_category = "underweight"
        elif calculated_bmi < 25:
            bmi_category = "normal"
        elif calculated_bmi < 30:
            bmi_category = "overweight"
        else:
            bmi_category = "obese"

    return render(
        request,
        "profiles/profile_edit.html",
        {
            "form": serializer,
            "profile": profile,
            "medications": medications,
            "contacts": contacts,
            "medical_events": medical_events,
            "calculated_bmi": calculated_bmi,
            "bmi_category": bmi_category,
        },
    )


@login_required
def personal_profile_edit_view(request):
    """Edit personal profile - personal details and physical info."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        profile = MedicalProfile.objects.create(user=request.user)

    if request.method == "POST":
        # Create mutable copy of POST data
        post_data = request.POST.copy()

        serializer = MedicalProfileSerializer(profile, data=post_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Personal profile updated successfully.")
            return redirect("dashboard")
    else:
        serializer = MedicalProfileSerializer(profile)

    # Calculate BMI
    calculated_bmi = None
    bmi_category = None
    if profile.height and profile.weight:
        height_m = profile.height / 100
        calculated_bmi = round(profile.weight / (height_m**2), 1)
        if calculated_bmi < 18.5:
            bmi_category = "underweight"
        elif calculated_bmi < 25:
            bmi_category = "normal"
        elif calculated_bmi < 30:
            bmi_category = "overweight"
        else:
            bmi_category = "obese"

    return render(
        request,
        "profiles/personal_profile_edit.html",
        {
            "form": serializer,
            "profile": profile,
            "calculated_bmi": calculated_bmi,
            "bmi_category": bmi_category,
        },
    )


@login_required
def medications_view(request):
    """View and manage medications."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    medications = profile.medications.all()
    return render(request, "profiles/medications.html", {"medications": medications})


@login_required
def medication_add_view(request):
    """Add a new medication."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    if request.method == "POST":
        serializer = MedicationSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save(profile=profile)
            messages.success(request, "Medication added successfully.")
            return redirect("medications")
    else:
        serializer = MedicationSerializer()

    return render(
        request, "profiles/medication_form.html", {"form": serializer, "action": "Add"}
    )


@login_required
def medication_edit_view(request, medication_id):
    """Edit an existing medication."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    # Get the medication and ensure it belongs to the user's profile
    medication = get_object_or_404(Medication, id=medication_id, profile=profile)

    if request.method == "POST":
        serializer = MedicationSerializer(medication, data=request.POST, partial=True)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Medication updated successfully.")
            return redirect("medications")
    else:
        serializer = MedicationSerializer(medication)

    return render(
        request,
        "profiles/medication_form.html",
        {"form": serializer, "action": "Edit", "medication": medication},
    )


@login_required
def medication_delete_view(request, medication_id):
    """Delete a medication."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    # Get the medication and ensure it belongs to the user's profile
    medication = get_object_or_404(Medication, id=medication_id, profile=profile)

    if request.method == "POST":
        medication.delete()
        messages.success(request, "Medication deleted successfully.")
        return redirect("medications")

    # If GET request, show confirmation page
    return render(
        request, "profiles/medication_confirm_delete.html", {"medication": medication}
    )


@login_required
def contacts_view(request):
    """View and manage emergency contacts."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    contacts = profile.emergency_contacts.all()
    can_add = contacts.count() < 2

    return render(
        request,
        "profiles/contacts.html",
        {"contacts": contacts, "can_add": can_add, "max_contacts": 2},
    )


@login_required
def contact_add_view(request):
    """Add a new emergency contact."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    # Enforce max 2 contacts at view level
    if profile.emergency_contacts.count() >= 2:
        messages.error(request, "Maximum of 2 emergency contacts allowed.")
        return redirect("emergency-contacts")

    if request.method == "POST":
        serializer = EmergencyContactSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save(profile=profile)
            messages.success(request, "Emergency contact added successfully.")
            return redirect("emergency-contacts")
    else:
        serializer = EmergencyContactSerializer()

    return render(
        request, "profiles/contact_form.html", {"form": serializer, "action": "Add"}
    )


@login_required
def contact_edit_view(request, contact_id):
    """Edit an existing emergency contact."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    # Get the contact and ensure it belongs to the user's profile
    contact = get_object_or_404(EmergencyContact, id=contact_id, profile=profile)

    if request.method == "POST":
        serializer = EmergencyContactSerializer(
            contact, data=request.POST, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Contact updated successfully.")
            return redirect("emergency-contacts")
    else:
        serializer = EmergencyContactSerializer(contact)

    return render(
        request,
        "profiles/contact_form.html",
        {"form": serializer, "action": "Edit", "contact": contact},
    )


@login_required
def contact_delete_view(request, contact_id):
    """Delete an emergency contact."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    # Get the contact and ensure it belongs to the user's profile
    contact = get_object_or_404(EmergencyContact, id=contact_id, profile=profile)

    if request.method == "POST":
        contact.delete()
        messages.success(request, "Contact deleted successfully.")
        return redirect("emergency-contacts")

    # If GET request, show confirmation (inline modal handled in template)
    return redirect("emergency-contacts")


@login_required
def events_view(request):
    """View medical history/events."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    events = profile.medical_events.all()
    return render(request, "profiles/events.html", {"events": events})


@login_required
def event_add_view(request):
    """Add a new medical event."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    if request.method == "POST":
        serializer = MedicalEventSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save(profile=profile)
            messages.success(request, "Medical event added successfully.")
            return redirect("events")
    else:
        serializer = MedicalEventSerializer()

    return render(
        request, "profiles/event_form.html", {"form": serializer, "action": "Add"}
    )


@login_required
def event_edit_view(request, event_id):
    """Edit an existing medical event."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    # Get the event and ensure it belongs to the user's profile
    event = get_object_or_404(MedicalEvent, id=event_id, profile=profile)

    if request.method == "POST":
        serializer = MedicalEventSerializer(event, data=request.POST, partial=True)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Medical event updated successfully.")
            return redirect("events")
    else:
        serializer = MedicalEventSerializer(event)

    return render(
        request,
        "profiles/event_form.html",
        {"form": serializer, "action": "Edit", "event": event},
    )


@login_required
def event_delete_view(request, event_id):
    """Delete a medical event."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    # Get the event and ensure it belongs to the user's profile
    event = get_object_or_404(MedicalEvent, id=event_id, profile=profile)

    if request.method == "POST":
        event.delete()
        messages.success(request, "Medical event deleted successfully.")
        return redirect("events")

    # If GET request, show confirmation (inline modal handled in template)
    return redirect("events")


def emergency_scan_template_view(request, public_id):
    """
    Public emergency view - HTML version for NFC/QR scanning.
    Returns life-saving data WITHOUT requiring authentication.
    Shows data based on user role:
    - Anonymous/User: Emergency data only (blood type, allergies, medications, contacts)
    - Doctor: Full medical data including history, chronic diseases
    - Engineer: Equipment/maintenance info + emergency data
    - Admin: All data

    CACHED: Uses Django cache for improved performance.
    Cache key varies by public_id and user role.
    Performance: ~2 queries instead of 10+ for full profile data.
    """
    # ======= FIRST: Check for embedded data in URL for INSTANT display =======
    embedded_data = request.GET.get("d")
    if embedded_data:
        decoded = decode_emergency_data(embedded_data)
        if decoded:
            # Verify the short ID matches
            if str(public_id).startswith(decoded.get("short_id", "")):
                # Calculate age from embedded date of birth
                embedded_age = None
                if decoded.get("date_of_birth"):
                    from datetime import date

                    try:
                        dob = decoded["date_of_birth"]
                        if isinstance(dob, str):
                            dob = date.fromisoformat(dob)
                        today = date.today()
                        embedded_age = (
                            today.year
                            - dob.year
                            - ((today.month, today.day) < (dob.month, dob.day))
                        )
                    except:
                        pass

                # Calculate BMI from embedded height/weight
                embedded_bmi = None
                embedded_bmi_category = None
                if (
                    decoded.get("height")
                    and decoded.get("height") > 0
                    and decoded.get("weight")
                    and decoded.get("weight") > 0
                ):
                    height_m = decoded["height"] / 100
                    embedded_bmi = round(decoded["weight"] / (height_m**2), 1)
                    if embedded_bmi:
                        if embedded_bmi < 18.5:
                            embedded_bmi_category = "underweight"
                        elif embedded_bmi < 25:
                            embedded_bmi_category = "normal"
                        elif embedded_bmi < 30:
                            embedded_bmi_category = "overweight"
                        else:
                            embedded_bmi_category = "obese"

                # Use embedded data for instant display (no DB hit!)
                context = {
                    "profile": None,  # Will use embedded data
                    "embedded_data": decoded,
                    "medications": [],
                    "contacts": [],
                    "medical_events": None,
                    "user_role": "user",
                    "show_basic_emergency": True,
                    "show_full_medical": False,
                    "show_engineer_info": False,
                    "show_insurance": False,
                    "national_id_masked": None,
                    "is_embedded": True,  # Flag to use embedded data in template
                    "is_profile_owner": False,
                    "calculated_age": embedded_age,
                    "calculated_bmi": embedded_bmi,
                    "bmi_category": embedded_bmi_category,
                }
                return render(request, "profiles/emergency_scan.html", context)

    # ======= No embedded data - fetch from cache or database =======
    # Get user role using utility function
    user_role = get_user_role(request.user)

    # Cache key varies by profile and role
    cache_key = f"emergency_profile_{public_id}_role_{user_role}"

    # Try to get from cache
    cached_context = cache.get(cache_key)
    if cached_context is not None:
        # Add role info for template
        cached_context["user_role"] = user_role
        # Check if user is the profile owner
        is_profile_owner = False
        if request.user.is_authenticated:
            try:
                if (
                    request.user.medical_profile
                    and request.user.medical_profile.public_id == public_id
                ):
                    is_profile_owner = True
            except MedicalProfile.DoesNotExist:
                is_profile_owner = False
        cached_context["is_profile_owner"] = is_profile_owner
        # Update visibility for owners
        if is_profile_owner:
            cached_context["show_full_medical"] = True
            cached_context["show_engineer_info"] = True
            cached_context["show_insurance"] = True
        return render(request, "profiles/emergency_scan.html", cached_context)

    # Optimized query: single query for profile+user, plus prefetched related data
    try:
        profile = (
            MedicalProfile.objects.select_related("user")
            .prefetch_related(
                Prefetch(
                    "medications",
                    # Get all medications - filter by is_active property in template
                    queryset=Medication.objects.all(),
                    to_attr="active_meds_list",
                ),
                "emergency_contacts",
                Prefetch(
                    "medical_events",
                    queryset=MedicalEvent.objects.all(),
                    to_attr="all_events",
                ),
            )
            .get(public_id=public_id)
        )
    except MedicalProfile.DoesNotExist:
        return render(request, "profiles/emergency_not_found.html", status=404)

    # Get user role (default to 'user' for anonymous)
    user_role = "user"
    accessed_by = None
    is_profile_owner = False
    if request.user.is_authenticated:
        try:
            user_role = getattr(request.user, "profile_role", "user")
            accessed_by = request.user
            # Check if user owns this profile
            try:
                if (
                    request.user.medical_profile
                    and request.user.medical_profile.public_id == profile.public_id
                ):
                    is_profile_owner = True
            except MedicalProfile.DoesNotExist:
                is_profile_owner = False
        except AttributeError:
            user_role = "user"

    # Log access if premium feature is enabled
    if profile.premium_access_logging:
        from .models import ProfileAccessLog

        ProfileAccessLog.objects.create(
            profile=profile,
            accessed_by=accessed_by,
            access_role=user_role,
            access_type="emergency",
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

    # Determine data visibility based on role
    show_basic_emergency = True  # Everyone sees this
    show_full_medical = (
        user_role in ["doctor", "admin"] or is_profile_owner
    )  # Doctors, admins, and owners
    show_engineer_info = (
        user_role in ["engineer", "admin"] or is_profile_owner
    )  # Engineers, admins, and owners
    show_insurance = (
        user_role
        in [
            "doctor",
            "admin",
            "engineer",
        ]
        or is_profile_owner
    )  # More access for medical/worker or owners

    # Use prefetched active medications (already filtered in query)
    medications = profile.active_meds_list

    # Use prefetched emergency contacts (max 2)
    contacts = list(profile.emergency_contacts.all()[:2])

    # Use prefetched medical events (for doctors/admins)
    medical_events = profile.all_events if show_full_medical else None

    # Masked National ID for engineers/admins (show first 4 and last 4 digits)
    national_id_masked = None
    if show_engineer_info and profile.user.national_id:
        nat_id = profile.user.national_id
        national_id_masked = f"{nat_id[:4]}****{nat_id[-4:]}"

    # Calculate age from date of birth
    calculated_age = None
    if profile.user.date_of_birth:
        from datetime import date

        today = date.today()
        calculated_age = (
            today.year
            - profile.user.date_of_birth.year
            - (
                (today.month, today.day)
                < (profile.user.date_of_birth.month, profile.user.date_of_birth.day)
            )
        )

    # Calculate BMI
    calculated_bmi = None
    if profile.height and profile.height > 0 and profile.weight and profile.weight > 0:
        height_m = profile.height / 100  # Convert cm to m
        calculated_bmi = round(profile.weight / (height_m**2), 1)

    # Determine BMI category
    bmi_category = None
    if calculated_bmi:
        if calculated_bmi < 18.5:
            bmi_category = "underweight"
        elif calculated_bmi < 25:
            bmi_category = "normal"
        elif calculated_bmi < 30:
            bmi_category = "overweight"
        else:
            bmi_category = "obese"

    context = {
        "profile": profile,
        "medications": medications,
        "contacts": contacts,
        "medical_events": medical_events,
        "user_role": user_role,
        "show_basic_emergency": show_basic_emergency,
        "show_full_medical": show_full_medical,
        "show_engineer_info": show_engineer_info,
        "show_insurance": show_insurance,
        "national_id_masked": national_id_masked,
        "is_profile_owner": is_profile_owner,
        "calculated_age": calculated_age,
        "calculated_bmi": calculated_bmi,
        "bmi_category": bmi_category,
    }
    # Cache the context for 15 minutes (900 seconds)
    # This dramatically speeds up repeated scans of the same profile
    cache.set(cache_key, context, 900)

    return render(request, "profiles/emergency_scan.html", context)


# ======= HTMX Partial Views for Fast Loading =======


def htmx_emergency_medications(request, public_id):
    """
    HTMX endpoint for loading medications section.
    Returns partial HTML for medications list.
    """
    try:
        profile = MedicalProfile.objects.prefetch_related(
            # Get all medications - filter by is_active property in template
            Prefetch("medications", queryset=Medication.objects.all())
        ).get(public_id=public_id)

        # Get all medications and let template filter by is_active property
        medications = profile.medications.all()

        # Check if HTMX request
        if request.headers.get("HX-Request"):
            return render(
                request,
                "profiles/partials/emergency_medications.html",
                {"medications": medications},
            )

        return JsonResponse(
            {
                "medications": list(
                    medications.values("name", "dosage", "frequency", "notes")
                )
            }
        )
    except MedicalProfile.DoesNotExist:
        if request.headers.get("HX-Request"):
            return render(request, "profiles/emergency_not_found.html", status=404)
        return JsonResponse({"error": "Profile not found"}, status=404)


def htmx_emergency_contacts(request, public_id):
    """
    HTMX endpoint for loading emergency contacts section.
    Returns partial HTML for contacts list.
    """
    try:
        profile = MedicalProfile.objects.prefetch_related("emergency_contacts").get(
            public_id=public_id
        )
        contacts = profile.emergency_contacts.all()[:2]

        if request.headers.get("HX-Request"):
            return render(
                request,
                "profiles/partials/emergency_contacts.html",
                {"contacts": contacts},
            )

        return JsonResponse(
            {
                "contacts": list(
                    contacts.values(
                        "name", "phone_number", "relationship", "is_primary"
                    )
                )
            }
        )
    except MedicalProfile.DoesNotExist:
        if request.headers.get("HX-Request"):
            return render(request, "profiles/emergency_not_found.html", status=404)
        return JsonResponse({"error": "Profile not found"}, status=404)


def htmx_emergency_history(request, public_id):
    """
    HTMX endpoint for loading medical history section.
    Returns partial HTML for medical events list.
    """
    # Use utility function for role detection (prevents role spoofing)
    user_role = get_user_role(request.user)

    # Only doctors and admins can see full medical history
    show_full_medical = user_role in ["doctor", "admin"]

    if not show_full_medical:
        if request.headers.get("HX-Request"):
            return render(
                request, "profiles/partials/emergency_history_restricted.html"
            )
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        profile = MedicalProfile.objects.prefetch_related(
            Prefetch(
                "medical_events", queryset=MedicalEvent.objects.order_by("-date")[:10]
            )
        ).get(public_id=public_id)

        medical_events = profile.medical_events.all()[:10]

        if request.headers.get("HX-Request"):
            return render(
                request,
                "profiles/partials/emergency_history.html",
                {"medical_events": medical_events},
            )

        return JsonResponse(
            {
                "events": list(
                    medical_events.values("title", "event_type", "date", "notes")
                )
            }
        )
    except MedicalProfile.DoesNotExist:
        if request.headers.get("HX-Request"):
            return render(request, "profiles/emergency_not_found.html", status=404)
        return JsonResponse({"error": "Profile not found"}, status=404)


def htmx_emergency_physical(request, public_id):
    """
    HTMX endpoint for loading physical info section.
    Returns partial HTML for height/weight.
    """
    try:
        profile = MedicalProfile.objects.get(public_id=public_id)

        if request.headers.get("HX-Request"):
            return render(
                request,
                "profiles/partials/emergency_physical.html",
                {"profile": profile},
            )

        return JsonResponse({"height": profile.height, "weight": profile.weight})
    except MedicalProfile.DoesNotExist:
        if request.headers.get("HX-Request"):
            return render(request, "profiles/emergency_not_found.html", status=404)
        return JsonResponse({"error": "Profile not found"}, status=404)


# ======= Emergency Alert View =======


@login_required
@csrf_exempt
@require_http_methods(["POST"])
@ratelimit(key="ip", rate="5/m", method="POST")
def emergency_alert_view(request):
    """
    Handle emergency alert from emergency page.
    Notifies emergency contacts with location data.
    """
    import json

    try:
        data = json.loads(request.body)
        profile_id = data.get("profile_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    try:
        profile = MedicalProfile.objects.get(public_id=profile_id)
    except MedicalProfile.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Profile not found"}, status=404
        )

    # Get emergency contacts
    contacts = profile.emergency_contacts.all()

    if not contacts:
        return JsonResponse(
            {"success": False, "message": "No emergency contacts"}, status=400
        )

    # In production, you would send SMS/Email notifications here
    # For now, we'll just log and return success
    location_info = ""
    if latitude and longitude:
        location_info = f"Location: https://maps.google.com/?q={latitude},{longitude}"

    # Log the alert (in production, integrate with SMS/Email service)
    logger.warning(f"EMERGENCY ALERT for {profile.user.username}: {location_info}")

    return JsonResponse(
        {
            "success": True,
            "message": f"Alert sent to {contacts.count()} emergency contact(s)",
        }
    )


# ======= Doctor Portal Views =======


@login_required
def doctor_portal_view(request):
    """
    Doctor portal - search for patient profiles by national ID.
    Only accessible to users with doctor or admin profile role.
    """
    # Check if user is a doctor
    if request.user.profile_role not in ["doctor", "admin"]:
        messages.error(request, "Access denied. Doctor account required.")
        return redirect("dashboard")

    search_results = None
    search_query = None

    if request.method == "GET" and "national_id" in request.GET:
        national_id = request.GET.get("national_id", "").strip()

        if len(national_id) == 14 and national_id.isdigit():
            search_query = national_id
            # Search by national ID
            from accounts.models import SyraUser

            try:
                user = SyraUser.objects.get(national_id=national_id)
                profile = MedicalProfile.objects.get(user=user)
                search_results = {
                    "user": user,
                    "profile": profile,
                }
            except SyraUser.DoesNotExist:
                messages.error(request, "No user found with this National ID.")
            except MedicalProfile.DoesNotExist:
                messages.error(request, "User found but no medical profile exists.")
        elif national_id:
            messages.error(request, "National ID must be exactly 14 digits.")

    context = {
        "search_results": search_results,
        "search_query": search_query,
    }
    return render(request, "profiles/doctor_portal.html", context)


@login_required
def doctor_add_medical_event(request, public_id):
    """
    Doctor can add a medical event to a patient's profile.
    Event is set to pending approval by default.
    """
    # Check if user is a doctor
    if request.user.profile_role not in ["doctor", "admin"]:
        messages.error(request, "Access denied. Doctor account required.")
        return redirect("dashboard")

    try:
        profile = MedicalProfile.objects.get(public_id=public_id)
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect("doctor-portal")

    if request.method == "POST":
        serializer = MedicalEventSerializer(data=request.POST)
        if serializer.is_valid():
            event = serializer.save(profile=profile)
            event.added_by_doctor = request.user
            event.pending_approval = True
            event.is_approved = False
            event.save()
            messages.success(request, "Medical event added. Pending user approval.")
            return redirect("doctor-portal")
    else:
        serializer = MedicalEventSerializer()

    return render(
        request,
        "profiles/doctor_add_event.html",
        {
            "form": serializer,
            "profile": profile,
        },
    )


@login_required
def doctor_add_medication(request, public_id):
    """
    Doctor can add a medication to a patient's profile.
    Medication is set to pending approval by default.
    """
    # Check if user is a doctor
    if request.user.profile_role not in ["doctor", "admin"]:
        messages.error(request, "Access denied. Doctor account required.")
        return redirect("dashboard")

    try:
        profile = MedicalProfile.objects.get(public_id=public_id)
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect("doctor-portal")

    if request.method == "POST":
        serializer = MedicationSerializer(data=request.POST)
        if serializer.is_valid():
            med = serializer.save(profile=profile)
            med.added_by_doctor = request.user
            med.pending_approval = True
            med.is_approved = False
            med.save()
            messages.success(request, "Medication added. Pending user approval.")
            return redirect("doctor-portal")
    else:
        serializer = MedicationSerializer()

    return render(
        request,
        "profiles/doctor_add_medication.html",
        {
            "form": serializer,
            "profile": profile,
        },
    )


# ======= User Approval Views =======


@login_required
def pending_approvals_view(request):
    """
    User view to see and approve/reject items added by doctors.
    """
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, "Please create a medical profile first.")
        return redirect("dashboard")

    # Get items pending approval
    pending_medications = profile.medications.filter(pending_approval=True)
    pending_contacts = profile.emergency_contacts.filter(pending_approval=True)
    pending_events = profile.medical_events.filter(pending_approval=True)

    context = {
        "pending_medications": pending_medications,
        "pending_contacts": pending_contacts,
        "pending_events": pending_events,
    }
    return render(request, "profiles/pending_approvals.html", context)


@login_required
@require_http_methods(["POST"])
def approve_item_view(request):
    """
    Approve a doctor-added item.
    """
    import json

    try:
        data = json.loads(request.body)
        item_type = data.get("item_type")
        item_id = data.get("item_id")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        return JsonResponse({"success": False, "message": "No profile"}, status=400)

    if item_type == "medication":
        item = get_object_or_404(Medication, id=item_id, profile=profile)
    elif item_type == "contact":
        item = get_object_or_404(EmergencyContact, id=item_id, profile=profile)
    elif item_type == "event":
        item = get_object_or_404(MedicalEvent, id=item_id, profile=profile)
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid item type"}, status=400
        )

    item.is_approved = True
    item.pending_approval = False
    item.approved_at = timezone.now()
    item.save()

    return JsonResponse({"success": True, "message": "Item approved"})


@login_required
@require_http_methods(["POST"])
def reject_item_view(request):
    """
    Reject/delete a doctor-added item.
    """
    import json

    try:
        data = json.loads(request.body)
        item_type = data.get("item_type")
        item_id = data.get("item_id")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        return JsonResponse({"success": False, "message": "No profile"}, status=400)

    if item_type == "medication":
        item = get_object_or_404(Medication, id=item_id, profile=profile)
    elif item_type == "contact":
        item = get_object_or_404(EmergencyContact, id=item_id, profile=profile)
    elif item_type == "event":
        item = get_object_or_404(MedicalEvent, id=item_id, profile=profile)
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid item type"}, status=400
        )

    item.delete()

    return JsonResponse({"success": True, "message": "Item rejected and removed"})
