from django.shortcuts import render, get_object_or_404
from django.views import View
from rest_framework import generics
from .models import MedicalProfile
from .serializers import MedicalProfileSerializer, InsuranceCardSerializer


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
