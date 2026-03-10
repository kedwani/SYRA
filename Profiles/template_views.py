"""
Profiles/template_views.py
"""

import base64
import mimetypes

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    BloodType,
    EmergencyContact,
    MedicalEvent,
    MedicalProfile,
    Medication,
)

User = get_user_model()


def _get_profile_or_404(username):
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(MedicalProfile, user=profile_user)
    return profile_user, profile


def _is_owner(request, profile_user):
    return request.user == profile_user


@login_required(login_url="web:login")
def dashboard_view(request, username):
    profile_user, profile = _get_profile_or_404(username)
    return render(
        request,
        "profiles/dashboard.html",
        {
            "profile_user": profile_user,
            "profile": profile,
            "is_owner": _is_owner(request, profile_user),
            "contacts": profile.emergency_contacts.all(),
            "medications": profile.medications.all(),
            "history": profile.medical_history.all(),
            "contact_count": profile.emergency_contacts.count(),
            "med_count": profile.medications.count(),
            "history_count": profile.medical_history.count(),
        },
    )


@login_required(login_url="web:login")
def edit_profile_view(request, username):
    profile_user, profile = _get_profile_or_404(username)
    if not _is_owner(request, profile_user):
        messages.error(request, "You can only edit your own profile.")
        return redirect("web:dashboard", username=username)
    return render(
        request,
        "profiles/edit.html",
        {
            "profile_user": profile_user,
            "profile": profile,
            "contacts": profile.emergency_contacts.all(),
            "medications": profile.medications.all(),
            "history": profile.medical_history.all(),
            "blood_type_choices": BloodType.choices,
        },
    )


@login_required(login_url="web:login")
def update_general_view(request, username):
    profile_user, profile = _get_profile_or_404(username)
    if not _is_owner(request, profile_user):
        return redirect("web:dashboard", username=username)
    if request.method == "POST":
        profile.blood_type = request.POST.get("blood_type", profile.blood_type)
        profile.gender = request.POST.get("gender", profile.gender)
        profile.date_of_birth = request.POST.get("date_of_birth") or None
        profile.allergies = request.POST.get("allergies", "").strip()
        profile.general_notes = request.POST.get("general_notes", "").strip()
        profile.save()
        messages.success(request, "General information saved.")
    return redirect("web:edit_profile", username=username)


@login_required(login_url="web:login")
def update_medical_view(request, username):
    profile_user, profile = _get_profile_or_404(username)
    if not _is_owner(request, profile_user):
        return redirect("web:dashboard", username=username)
    if request.method == "POST":
        profile.chronic_diseases = request.POST.get("chronic_diseases", "").strip()
        profile.immune_diseases = request.POST.get("immune_diseases", "").strip()
        profile.save()
        messages.success(request, "Medical conditions saved.")
    return redirect("web:edit_profile", username=username)


@login_required(login_url="web:login")
def add_contact_view(request, username):
    profile_user, profile = _get_profile_or_404(username)
    if not _is_owner(request, profile_user):
        return redirect("web:dashboard", username=username)
    if request.method == "POST":
        if profile.emergency_contacts.count() >= 2:
            messages.error(request, "Maximum 2 emergency contacts allowed.")
        else:
            EmergencyContact.objects.create(
                profile=profile,
                name=request.POST.get("name", "").strip(),
                relationship=request.POST.get("relationship", "").strip(),
                phone_number=request.POST.get("phone_number", "").strip(),
                priority=int(request.POST.get("priority", 1)),
            )
            messages.success(request, "Emergency contact added.")
    return redirect("web:edit_profile", username=username)


@login_required(login_url="web:login")
def delete_contact_view(request, username, pk):
    profile_user, profile = _get_profile_or_404(username)
    if not _is_owner(request, profile_user):
        return redirect("web:dashboard", username=username)
    if request.method == "POST":
        EmergencyContact.objects.filter(pk=pk, profile=profile).delete()
        messages.success(request, "Contact removed.")
    return redirect("web:edit_profile", username=username)


@login_required(login_url="web:login")
def add_medication_view(request, username):
    profile_user, profile = _get_profile_or_404(username)
    if not _is_owner(request, profile_user):
        return redirect("web:dashboard", username=username)
    if request.method == "POST":
        duration_raw = request.POST.get("duration_days", "").strip()
        Medication.objects.create(
            profile=profile,
            name=request.POST.get("name", "").strip(),
            dosage=request.POST.get("dosage", "").strip(),
            start_date=request.POST.get("start_date"),
            duration_days=int(duration_raw) if duration_raw else None,
        )
        messages.success(request, "Medication added.")
    return redirect("web:edit_profile", username=username)


@login_required(login_url="web:login")
def delete_medication_view(request, username, pk):
    profile_user, profile = _get_profile_or_404(username)
    if not _is_owner(request, profile_user):
        return redirect("web:dashboard", username=username)
    if request.method == "POST":
        Medication.objects.filter(pk=pk, profile=profile).delete()
        messages.success(request, "Medication removed.")
    return redirect("web:edit_profile", username=username)


@login_required(login_url="web:login")
def add_history_view(request, username):
    profile_user, profile = _get_profile_or_404(username)
    if not _is_owner(request, profile_user):
        return redirect("web:dashboard", username=username)
    if request.method == "POST":
        MedicalEvent.objects.create(
            profile=profile,
            event_type=request.POST.get("event_type", "Other"),
            description=request.POST.get("description", "").strip(),
            event_date=request.POST.get("event_date"),
            hospital=request.POST.get("hospital", "").strip(),
        )
        messages.success(request, "Medical event added.")
    return redirect("web:edit_profile", username=username)


@login_required(login_url="web:login")
def delete_history_view(request, username, pk):
    profile_user, profile = _get_profile_or_404(username)
    if not _is_owner(request, profile_user):
        return redirect("web:dashboard", username=username)
    if request.method == "POST":
        MedicalEvent.objects.filter(pk=pk, profile=profile).delete()
        messages.success(request, "Record removed.")
    return redirect("web:edit_profile", username=username)


@login_required(login_url="web:login")
def insurance_view(request, username):
    profile_user, profile = _get_profile_or_404(username)
    if not _is_owner(request, profile_user):
        messages.error(
            request, "Insurance data is only accessible to the profile owner."
        )
        return redirect("web:dashboard", username=username)

    insurance_image_b64 = None
    insurance_mime = "image/jpeg"

    if request.method == "POST":
        profile.insurance_company = request.POST.get("insurance_company", "").strip()
        upload = request.FILES.get("insurance_card_upload")
        if upload:
            profile.save_encrypted_insurance_image(upload)
        profile.save()
        messages.success(request, "Insurance information saved and encrypted.")
        return redirect("web:insurance", username=username)

    if profile.insurance_card_encrypted_path:
        try:
            raw_bytes = profile.get_decrypted_insurance_image()
            insurance_image_b64 = base64.b64encode(raw_bytes).decode("utf-8")
            mime, _ = mimetypes.guess_type(
                profile.insurance_card_encrypted_path.replace(".enc", "")
            )
            insurance_mime = mime or "image/jpeg"
        except Exception:
            messages.error(request, "Could not decrypt insurance image.")

    return render(
        request,
        "profiles/insurance.html",
        {
            "profile_user": profile_user,
            "profile": profile,
            "insurance_image_b64": insurance_image_b64,
            "insurance_mime": insurance_mime,
        },
    )


@login_required(login_url="web:login")
def search_view(request):
    query = request.GET.get("q", "").strip()
    result = None
    if query:
        result = (
            MedicalProfile.objects.select_related("user")
            .filter(user__username=query)
            .first()
            or MedicalProfile.objects.select_related("user")
            .filter(public_id=query)
            .first()
        )
    return render(request, "profiles/search.html", {"query": query, "result": result})


def emergency_view(request, public_id):
    profile = get_object_or_404(MedicalProfile, public_id=public_id)
    return render(
        request,
        "profiles/emergency.html",
        {
            "profile_user": profile.user,
            "profile": profile,
            "contacts": profile.emergency_contacts.all(),
            "medications": profile.medications.all(),
        },
    )
