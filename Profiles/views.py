from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from rest_framework import generics
from .models import MedicalProfile, ScanRecord
from .forms import MedicalProfileForm
from .serializers import MedicalProfileSerializer, InsuranceCardSerializer
from django.contrib.auth.decorators import login_required


# الصفحة الرئيسية (Index)
def index(request):
    return render(request, "profiles/index.html")


# دالة للحصول على الـ IP الخاص بالماسح
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# المتحكم في مسح السوار
def bracelet_handler(request, bracelet_id):
    profile, created = MedicalProfile.objects.get_or_create(bracelet_id=bracelet_id)

    # تسجيل عملية المسح في السجل
    ScanRecord.objects.create(
        profile=profile,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )

    if not profile.user:
        return render(request, "profiles/first_scan.html", {"bracelet_id": bracelet_id})

    return render(request, "profiles/profile_detail.html", {"profile": profile})


@login_required
def register_medical_info(request):
    profile, created = MedicalProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = MedicalProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile-web-view", user__username=request.user.username)
    else:
        form = MedicalProfileForm(instance=profile)
    return render(request, "profiles/register_info.html", {"form": form})


# عرض سجل المسح للمريض
@login_required
def scan_history_view(request):
    profile = get_object_or_404(MedicalProfile, user=request.user)
    scans = profile.scans.all().order_by("-scan_time")
    return render(request, "profiles/scan_history.html", {"scans": scans})


class ProfileWebView(View):
    def get(self, request, user__username):
        profile = get_object_or_404(MedicalProfile, user__username=user__username)
        return render(request, "profiles/profile_detail.html", {"profile": profile})


# --- API Views ---
class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = MedicalProfile.objects.all()
    serializer_class = MedicalProfileSerializer
    lookup_field = "user__username"


class InsuranceDetailView(generics.RetrieveAPIView):
    queryset = MedicalProfile.objects.all()
    serializer_class = InsuranceCardSerializer
    lookup_field = "user__username"
