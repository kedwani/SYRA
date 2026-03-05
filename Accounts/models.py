from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # إضافة حقول هامة لمريض الطوارئ
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
