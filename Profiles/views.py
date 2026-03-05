from rest_framework import generics
from .models import MedicalProfile
from .serializers import MedicalProfileSerializer, InsuranceSerializer
from rest_framework.permissions import IsAuthenticated


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = MedicalProfile.objects.all()
    serializer_class = MedicalProfileSerializer
    # لضمان أن كل مستخدم يشوف بروفايله بس (أو بروفايل الـ QR)
    lookup_field = "user__username"


class InsuranceDetailView(generics.RetrieveAPIView):
    queryset = MedicalProfile.objects.all()
    serializer_class = InsuranceSerializer
    lookup_field = "user__username"
