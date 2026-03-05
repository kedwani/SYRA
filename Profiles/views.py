from rest_framework import generics
from .models import MedicalProfile
from .serializers import MedicalProfileSerializer, InsuranceCardSerializer


# عرض وتعديل الملف الطبي (رؤية البيانات + تحديثها)
class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = MedicalProfile.objects.all()
    serializer_class = MedicalProfileSerializer
    lookup_field = "user__username"


# عرض صورة التأمين فقط (رابط منفصل بطلب خاص)
class InsuranceDetailView(generics.RetrieveAPIView):
    queryset = MedicalProfile.objects.all()
    serializer_class = InsuranceCardSerializer
    lookup_field = "user__username"
