from django.shortcuts import render, get_object_or_404, redirect
from .forms import MedicalProfileForm
from django.views import View
from rest_framework import generics
from .models import MedicalProfile
from .serializers import MedicalProfileSerializer, InsuranceCardSerializer


def index(request):
    return render(request, "profiles/index.html")


# صفحة التسجيل وتفعيل الأسورة
def register_medical_info(request):
    if request.method == "POST":
        form = MedicalProfileForm(request.POST)
        if form.is_valid():
            # هنا بنفترض إن المستخدم عمل Login أو بنربطه بيوزر جديد
            profile = form.save(commit=False)
            profile.user = request.user  # ربط البيانات باليوزر الحالي
            profile.save()
            return redirect("profile-web-view", user__username=request.user.username)
    else:
        form = MedicalProfileForm()
    return render(request, "profiles/register_info.html", {"form": form})


# عرض الصفحة للمستخدم (HTML)
class ProfileWebView(View):
    def get(self, request, user__username):
        profile = get_object_or_404(MedicalProfile, user__username=user__username)
        return render(request, "profiles/profile_detail.html", {"profile": profile})


# عرض وتعديل البيانات (API - JSON)
class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = MedicalProfile.objects.all()
    serializer_class = MedicalProfileSerializer
    lookup_field = "user__username"


# عرض صورة التأمين (API - JSON)
class InsuranceDetailView(generics.RetrieveAPIView):
    queryset = MedicalProfile.objects.all()
    serializer_class = InsuranceCardSerializer
    lookup_field = "user__username"
