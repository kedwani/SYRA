# Arabic Medical Terminology - SYRA Project

## Overview
This document standardizes Arabic medical terminology for the SYRA Medical ID project.
All terms use the definite article (ال) where appropriate in standard Arabic.

---

## Blood & Circulatory System (الدم والدورة الدموية)

| English | Arabic (Singular) | Arabic (Plural) | Notes |
|---------|-------------------|-----------------|-------|
| Blood Type | فصيلة الدم | فصيلة الدم | No plural needed |
| Blood Pressure | ضغط الدم | ضغط الدم | No plural needed |
| Heart Rate | معدل ضربات القلب | معدل ضربات القلب | No plural needed |
| Blood Type (A, B, AB, O) | فصيلة الدم | - | Use with type letter |

---

## Medical Conditions (الحالات الطبية)

| English | Arabic (Singular) | Arabic (Plural) | Notes |
|---------|-------------------|-----------------|-------|
| Allergy | الحساسية | الحساسيات | Use plural when listing multiple |
| Allergies | الحساسيات | الحساسيات | Use this form for field labels |
| Chronic Disease | المرض المزمن | الأمراض المزمنة | With definite article |
| Chronic Diseases | الأمراض المزمنة | الأمراض المزمنة | Use this form for field labels |
| Diabetes | السكري | السكري | Already definite form |
| Hypertension | ارتفاع ضغط الدم | - | - |
| Heart Disease | أمراض القلب | - | - |

---

## Medications (الأدوية)

| English | Arabic (Singular) | Arabic (Plural) | Notes |
|---------|-------------------|-----------------|-------|
| Medication | الدواء | الأدوية | - |
| Medications | الأدوية | الأدوية | Use this form for field labels |
| Dosage | الجرعة | الجرعات | - |
| Prescription | الوصفة الطبية | الوصفة الطبية | No plural needed |
| Frequency | التكرار | التكرارات | - |

---

## Emergency Terms (مصطلحات الطوارئ)

| English | Arabic | Notes |
|---------|--------|-------|
| Emergency | الطوارئ | Always plural form |
| Emergency Notes | ملاحظات الطوارئ | - |
| Emergency Contact | جهة اتصال الطوارئ | جهات اتصال الطوارئ for plural |
| Emergency Contacts | جهات اتصال الطوارئ | Use for field labels |
| Emergency Services | خدمات الطوارئ | - |
| First Aid | الإسعافات الأولية | - |

---

## Physical Information (المعلومات الجسدية)

| English | Arabic | Notes |
|---------|--------|-------|
| Height | الطول | - |
| Weight | الوزن | - |
| Height (cm) | الطول (سم) | - |
| Weight (kg) | الوزن (كجم) | - |

---

## Medical History (التاريخ الطبي)

| English | Arabic | Notes |
|---------|--------|-------|
| Medical History | التاريخ الطبي | - |
| Medical Event | الحدث الطبي | الأحداث الطبية for plural |
| Medical Events | الأحداث الطبية | - |
| Hospital | المستشفى | المستشفيات for plural |
| Date | التاريخ | - |
| Type | النوع | - |
| Title | العنوان | - |

---

## Personal Information (المعلومات الشخصية)

| English | Arabic | Notes |
|---------|--------|-------|
| First Name | الاسم الأول | - |
| Last Name | اسم العائلة | - |
| Full Name | الاسم الكامل | - |
| Date of Birth | تاريخ الميلاد | - |
| National ID | الرقم الوطني | - |
| Gender | النوع | - |
| Nationality | الجنسية | - |

---

## Insurance (التأمين)

| English | Arabic | Notes |
|---------|--------|-------|
| Insurance Information | معلومات التأمين | - |
| Insurance Provider | شركة التأمين | - |
| Insurance Number | رقم التأمين | - |

---

## Usage Rules

### 1. Plural vs Singular
- **Field Labels**: Always use plural form (e.g., "الأدوية" not "الدواء")
- **Single Item Display**: Use singular when showing one item
- **Lists**: Use plural when showing multiple items

### 2. Definite Article (ال)
- Use الـ (al) for:
  - Generic categories: الأمراض المزمنة, الأدوية
  - Standard terms: التأمين, الطوارئ
- Do NOT use for:
  - Proper nouns: مستشفى械 конкретні
  - Already definite forms: السكري

### 3. Translation Consistency
- Always check this glossary before adding new translations
- Update existing translations if they don't match

---

## Current Inconsistencies Found

### Must Fix in django.po:
| msgid | Current | Should Be |
|-------|---------|-----------|
| Allergies | الحساسية | الحساسيات |
| No allergies listed | لا توجد حساسية مذكورة | لا توجد حساسيات مذكورة |

---

## Recommended Review Items

These terms should be reviewed by a native Arabic-speaking medical professional:
1. Accuracy of medical terminology
2. Regional variations (Egyptian vs. Modern Standard Arabic)
3. Clarity for emergency responders

---

*Last Updated: 2026-03-18*
*For SYRA Project - Medical ID System*
