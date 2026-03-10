"""Template views for the Profiles app - Patient dashboard."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import MedicalProfile, Medication, EmergencyContact, MedicalEvent
from .serializers import (
    MedicalProfileSerializer, MedicationSerializer,
    EmergencyContactSerializer, MedicalEventSerializer
)


@login_required
def dashboard_view(request):
    """Patient dashboard - view and manage medical profile."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        profile = None
    
    context = {
        'profile': profile,
        'profile_serializer': MedicalProfileSerializer(profile).data if profile else None,
    }
    return render(request, 'profiles/dashboard.html', context)


@login_required
def profile_edit_view(request):
    """Edit medical profile."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        profile = MedicalProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        serializer = MedicalProfileSerializer(profile, data=request.POST, files=request.FILES, partial=True)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard')
    else:
        serializer = MedicalProfileSerializer(profile)
    
    return render(request, 'profiles/profile_edit.html', {'form': serializer})


@login_required
def medications_view(request):
    """View and manage medications."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, 'Please create a medical profile first.')
        return redirect('dashboard')
    
    medications = profile.medications.all()
    return render(request, 'profiles/medications.html', {'medications': medications})


@login_required
def medication_add_view(request):
    """Add a new medication."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, 'Please create a medical profile first.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        serializer = MedicationSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save(profile=profile)
            messages.success(request, 'Medication added successfully.')
            return redirect('medications')
    else:
        serializer = MedicationSerializer()
    
    return render(request, 'profiles/medication_form.html', {'form': serializer, 'action': 'Add'})


@login_required
def contacts_view(request):
    """View and manage emergency contacts."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, 'Please create a medical profile first.')
        return redirect('dashboard')
    
    contacts = profile.emergency_contacts.all()
    can_add = contacts.count() < 2
    
    return render(request, 'profiles/contacts.html', {
        'contacts': contacts,
        'can_add': can_add,
        'max_contacts': 2
    })


@login_required
def contact_add_view(request):
    """Add a new emergency contact."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, 'Please create a medical profile first.')
        return redirect('dashboard')
    
    # Enforce max 2 contacts at view level
    if profile.emergency_contacts.count() >= 2:
        messages.error(request, 'Maximum of 2 emergency contacts allowed.')
        return redirect('contacts')
    
    if request.method == 'POST':
        serializer = EmergencyContactSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save(profile=profile)
            messages.success(request, 'Emergency contact added successfully.')
            return redirect('contacts')
    else:
        serializer = EmergencyContactSerializer()
    
    return render(request, 'profiles/contact_form.html', {'form': serializer, 'action': 'Add'})


@login_required
def events_view(request):
    """View medical history/events."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, 'Please create a medical profile first.')
        return redirect('dashboard')
    
    events = profile.medical_events.all()
    return render(request, 'profiles/events.html', {'events': events})


@login_required
def event_add_view(request):
    """Add a new medical event."""
    try:
        profile = request.user.medical_profile
    except MedicalProfile.DoesNotExist:
        messages.error(request, 'Please create a medical profile first.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        serializer = MedicalEventSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save(profile=profile)
            messages.success(request, 'Medical event added successfully.')
            return redirect('events')
    else:
        serializer = MedicalEventSerializer()
    
    return render(request, 'profiles/event_form.html', {'form': serializer, 'action': 'Add'})


def emergency_scan_template_view(request, public_id):
    """
    Public emergency view - HTML version for NFC/QR scanning.
    Returns life-saving data WITHOUT requiring authentication.
    Excludes sensitive insurance/financial data.
    """
    try:
        profile = MedicalProfile.objects.get(public_id=public_id)
    except MedicalProfile.DoesNotExist:
        return render(request, 'profiles/emergency_not_found.html', status=404)
    
    # Get active medications
    medications = profile.medications.filter(is_active=True)
    
    # Get emergency contacts (max 2)
    contacts = profile.emergency_contacts.all()[:2]
    
    context = {
        'profile': profile,
        'medications': medications,
        'contacts': contacts,
    }
    return render(request, 'profiles/emergency_scan.html', context)
