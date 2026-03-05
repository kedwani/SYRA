from django import forms
from .models import MedicalProfile, EmergencyContact


class MedicalProfileForm(forms.ModelForm):
    class Meta:
        model = MedicalProfile
        fields = [
            "blood_type",
            "gender",
            "birth_date",
            "chronic_diseases",
            "medical_history",
            "notes",
        ]
        widgets = {
            "birth_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "blood_type": forms.Select(attrs={"class": "form-select"}),
            "chronic_diseases": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                    "placeholder": "مثال: سكر، ضغط..",
                }
            ),
            "medical_history": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }
