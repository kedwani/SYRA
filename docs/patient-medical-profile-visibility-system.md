# Patient Medical Profile Visibility System Design Document

## Executive Summary

This document outlines the complete design for a two-tier patient medical profile visibility system for the SYRA QR code-based emergency medical information application. The system provides:
- **Visibility Level 1**: Default Emergency View (Public Access) - instant loading, life-saving information for first responders
- **Visibility Level 2**: Doctor Expanded View (Verified Medical Professional) - comprehensive medical data after authentication

---

## 1. Current System Analysis

### Existing Implementation Overview

The current SYRA system already has foundational elements in place:

| Component | Status | Location |
|-----------|--------|----------|
| MedicalProfile model | ✅ Implemented | `profiles/models.py:9-201` |
| Visibility toggle fields | ✅ Implemented | `profiles/models.py:80-110` |
| EmergencyProfileSerializer | ✅ Implemented | `profiles/serializers.py:130-191` |
| ProfileAccessLog model | ✅ Implemented | `profiles/models.py:371-407` |
| Insurance image encryption | ✅ Implemented | `profiles/models.py:159-191` |
| Emergency scan view | ✅ Implemented | `profiles/views.py:200-220` |
| Doctor access check API | ✅ Implemented | `profiles/views.py:246-326` |

### Identified Issues (Potential Problem Sources)

After analyzing the codebase, I've identified **7 distinct sources** that could cause problems with the visibility system:

1. **Missing "Reveal All Data" Button Flow** - No explicit UI mechanism for doctors to request expanded data access
2. **No Warning Messages for Critical Fields** - No user feedback when patients try to hide blood type or allergies
3. **Incomplete Access Logging** - Expanded data access events aren't specifically logged as "doctor_reveal" type
4. **No Mandatory Field Enforcement** - System allows hiding critical emergency information without warnings
5. **Missing Doctor Authentication UI** - No clear login-to-reveal flow for the expanded view
6. **Privacy Toggle UX Gaps** - No clear indication of privacy implications when toggling fields
7. **No Emergency Notes Visibility Control** - Emergency notes field has no privacy toggle

---

## 2. Complete Field Lists

### 2.1 Visibility Level 1: Default Emergency View (Public Access)

This level displays immediately when first responders or bystanders scan a QR code. It prioritizes **simplicity, speed, and life-saving information**.

| Field | Data Type | Display Priority | Justification |
|-------|-----------|------------------|---------------|
| **Blood Type** | String (A+, A-, B+, etc.) | 🔴 CRITICAL - Top | Essential for emergency transfusions |
| **Severe Allergies** | Text | 🔴 CRITICAL - High | Prevents life-threatening allergic reactions |
| **Current Medications** | List | 🟠 HIGH - Medium | Prevents dangerous drug interactions |
| **Emergency Notes** | Text | 🟠 HIGH - Medium | Critical instructions for first responders |
| **Emergency Contacts** | List (max 2) | 🟡 STANDARD | Enables family notification |
| **Chronic Diseases** | Text | 🟡 STANDARD | Context for ongoing conditions |

**Display Requirements:**
- Load within 2 seconds on 3G connection
- Minimum font size: 18px for critical fields
- Color-coded urgency indicators (red/orange/yellow)
- Large touch targets for emergency buttons
- Works offline after initial load

### 2.2 Visibility Level 2: Doctor Expanded View (Verified Medical Professional)

This level reveals comprehensive medical data after verified physician authentication.

| Field | Data Type | Visibility Control | Category |
|-------|-----------|-------------------|----------|
| **All Level 1 Fields** | - | Always visible | Emergency |
| Full Medication List | List | `show_medications_public` | Medications |
| Medication Dosages | String | `show_medications_public` | Medications |
| Medication Frequency | String | `show_medications_public` | Medications |
| Medication Notes | Text | `show_medications_public` | Medications |
| Height | Integer (cm) | `show_physical_public` | Physical |
| Weight | Integer (kg) | `show_physical_public` | Physical |
| Chronic Diseases | Text | `show_history_public` | Medical History |
| Medical Events | List | `show_history_public` | Medical History |
| Event Dates | Date | `show_history_public` | Medical History |
| Event Descriptions | Text | `show_history_public` | Medical History |
| Hospital Names | Text | `show_history_public` | Medical History |
| Doctor Names | Text | `show_history_public` | Medical History |
| Insurance Provider | String | Always hidden from public | Insurance |
| Insurance Number | String | Always hidden from public | Insurance |
| Insurance Image | File | Always hidden from public | Insurance |
| Pending Medications | List | Always hidden from public | Doctor-only |
| Pending Events | List | Always hidden from public | Doctor-only |
| Pending Contacts | List | Always hidden from public | Doctor-only |
| Profile Access Logs | List | Always hidden from public | Audit |

---

## 3. Recommended Mandatory Public Fields

### 3.1 Mandatory Fields (Cannot Be Hidden)

The following fields are **strongly recommended as mandatory** public fields due to their critical importance in emergency situations:

| Field | Rationale | Risk Level if Hidden |
|-------|------------|---------------------|
| **Blood Type** | Essential for emergency blood transfusions; O- is universal donor | **LIFE-THREATENING** |
| **Severe Allergies** (anaphylaxis) | Prevents fatal allergic reactions to medications/foods | **LIFE-THREATENING** |
| **Emergency Notes** | Contains critical patient directives | **HIGH RISK** |

### 3.2 System Warning Implementation

When a patient attempts to hide critical emergency information, the system MUST display warnings:

#### Warning Message Design

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  IMPORTANT PRIVACY WARNING                                  │
├─────────────────────────────────────────────────────────────────┤
│  You are about to hide your BLOOD TYPE from public view.       │
│                                                                 │
│  In an emergency, first responders NEED this information       │
│  to make life-saving decisions about blood transfusions.       │
│                                                                 │
│  ⚠️  HIDING THIS INFORMATION COULD DELAY EMERGENCY TREATMENT  │
│                                                                 │
│  [  I understand the risks - Hide Blood Type  ]  [  Cancel  ] │
│                                                                 │
│  Your choice will be saved, but we strongly recommend          │
│  keeping this information visible for your safety.             │
└─────────────────────────────────────────────────────────────────┘
```

#### Warning Messages for Each Critical Field

| Field | Warning Title | Warning Message |
|-------|--------------|-----------------|
| **Blood Type** | ⚠️ Blood Type Warning | "You are about to hide your blood type. In emergencies, this information can be life-saving for blood transfusions. Hiding this could delay critical treatment." |
| **Severe Allergies** | ⚠️ Allergy Information Warning | "You are about to hide allergy information. First responders need this to avoid administering medications that could cause fatal allergic reactions." |
| **Emergency Notes** | ⚠️ Emergency Notes Warning | "You are about to hide your emergency notes. These contain critical instructions for first responders. Consider what information might be needed in an emergency." |

---

## 4. UX Design for "Reveal All Data" Button

### 4.1 Button Placement

The "Reveal All Data" button should be positioned:

1. **Primary Location**: Bottom of the Emergency View, before the "Find Nearby Hospitals" button
2. **Secondary Location**: Top-right corner as an icon (less prominent)

#### Mockup Layout

```
┌──────────────────────────────────────────────────────────────┐
│  🔴 EMERGENCY MEDICAL ID                                      │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌────────────────────────────────────────┐  │
│  │   BLOOD     │  │           ALLERGIES                    │  │
│  │     A+      │  │     ⚠️ Penicillin, Shellfish            │  │
│  │             │  │                                         │  │
│  └─────────────┘  └────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 💊 CURRENT MEDICATIONS                                     ││
│  │ [ Metformin 500mg ] [ Lisinopril 10mg ] [ Aspirin 81mg ]   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  📞 EMERGENCY CONTACTS                                         ││
│  [John Doe - Wife] 📱 Call    [Jane Doe - Sister] 📱 Call      ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ╔═══════════════════════════════════════════════════════════╗│
│  ║  🔒 DOCTOR ACCESS                                           ║│
│  ║  Sign in to view complete medical history, medications,    ║│
│  ║  and insurance details.                                    ║│
│  ║                                                               ║│
│  ║  [      👨‍⚕️  REVEAL ALL DATA (Doctor Login)      ]        ║│
│  ╚═══════════════════════════════════════════════════════════╝│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📍 SEND EMERGENCY ALERT           🏥 FIND NEARBY HOSPITALS  ││
│  └─────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Button Styling Requirements

| Property | Value | Rationale |
|----------|-------|-----------|
| **Background** | Gradient: `#1E40AF` to `#3B82F6` (Blue) | Professional, medical, trustworthy |
| **Text Color** | White | High contrast |
| **Font Size** | 16px bold | Readable on mobile |
| **Padding** | 16px vertical, 24px horizontal | Easy touch target |
| **Border Radius** | 12px | Modern, friendly appearance |
| **Icon** | Medical shield icon (left of text) | Clear context |
| **Shadow** | `0 4px 6px rgba(0,0,0,0.1)` | Subtle elevation |
| **Hover State** | Slightly darker, scale 1.02 | Interactive feedback |
| **Disabled State** | Gray, 50% opacity | When already expanded |

### 4.3 Interaction Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     DOCTOR EXPANDED VIEW FLOW                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STEP 1: Initial State                                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Doctor visits emergency scan page                         │ │
│  │ Sees: "Sign in to view complete medical history"          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           ↓                                     │
│  STEP 2: Click "Reveal All Data"                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Modal opens:                                                │ │
│  │ ┌─────────────────────────────────────────────────────────┐│ │
│  │ │  👨‍⚕️ Doctor Authentication                              ││ │
│  │ │                                                          ││ │
│  │ │  Email:    [________________]                           ││ │
│  │ │  Password: [________________]                           ││ │
│  │ │                                                          ││ │
│  │ │  License #: [________________]  (Optional)               ││ │
│  │ │                                                          ││ │
│  │ │  [Cancel]                    [Verify & Reveal]         ││ │
│  │ └─────────────────────────────────────────────────────────┘│ │
│  └───────────────────────────────────────────────────────────┘ │
│                           ↓                                     │
│  STEP 3: Verification                                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ System checks:                                              │ │
│  │ 1. Valid credentials                                       │ │
│  │ 2. Doctor role assigned                                     │ │
│  │ 3. License number verified (if required)                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           ↓                                     │
│  STEP 4: Success - Expanded View Revealed                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Page transitions with animation:                          │ │
│  │ • Blue glow effect on revealed sections                    │ │
│  │ • "CONFIDENTIAL - Doctor Access" banner                    │ │
│  │ • Full medical history visible                             │ │
│  │ • Insurance details visible                                 │ │
│  │ • Access logged with timestamp                             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           ↓                                      │
│  STEP 5: Access Logged                                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ ProfileAccessLog created:                                   │ │
│  │  • access_type: "doctor_reveal"                            │ │
│  │  • accessed_by: doctor user                                 │ │
│  │  • access_role: "doctor"                                   │ │
│  │  • ip_address, user_agent recorded                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.4 Animation & Transition Effects

```css
/* Reveal Animation */
.doctor-expanded-view {
    animation: revealSlideDown 0.4s ease-out;
    border: 2px solid #3B82F6;
    background: linear-gradient(180deg, #EFF6FF 0%, #DBEAFE 100%);
}

@keyframes revealSlideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Confidentiality Banner */
.confidential-banner {
    background: linear-gradient(90deg, #1E40AF, #3B82F6);
    color: white;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
    text-align: center;
    border-radius: 8px;
    margin-bottom: 16px;
}
```

---

## 5. Privacy Control System Implementation

### 5.1 Current Visibility Controls (Already Implemented)

The system already has these privacy toggle fields in [`profiles/models.py:80-110`](profiles/models.py:80):

```python
# Visibility Controls - User controls which sections are public vs doctor-only
show_blood_type_public = models.BooleanField(default=True, ...)
show_allergies_public = models.BooleanField(default=True, ...)
show_medications_public = models.BooleanField(default=True, ...)
show_contacts_public = models.BooleanField(default=True, ...)
show_physical_public = models.BooleanField(default=False, ...)
show_history_public = models.BooleanField(default=False, ...)
```

### 5.2 Recommended Additions

```python
# Add to MedicalProfile model
show_emergency_notes_public = models.BooleanField(
    default=True,
    verbose_name="Show Emergency Notes to Public",
    help_text="Anyone can view emergency notes in emergencies"
)
```

### 5.3 Privacy Toggle UI Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    🔒 PRIVACY SETTINGS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PUBLIC EMERGENCY VIEW (Visible to Everyone)                   │
│  ───────────────────────────────────────────────────────────   │
│                                                                 │
│  🔴 Blood Type                                    [ ● ON ]      │
│     Required for emergency transfusions                        │
│     ⚠️ Cannot be hidden - always visible                       │
│                                                                 │
│  🔴 Severe Allergies (Anaphylaxis)             [ ● ON ]        │
│     Critical for medication safety                              │
│     ⚠️ Warning required if turned off                          │
│                                                                 │
│  💊 Current Medications                          [ ○ OFF ]     │
│     Anyone scanning your code can see medications              │
│     [Change]                                                    │
│                                                                 │
│  📝 Emergency Notes                                 [ ● ON ]    │
│     Instructions for first responders                           │
│     [Change]                                                    │
│                                                                 │
│  📞 Emergency Contacts                           [ ● ON ]     │
│     Anyone can see and call your contacts                       │
│     [Change]                                                    │
│                                                                 │
│  DOCTOR-ONLY VIEW (Requires Verified Doctor Login)             │
│  ───────────────────────────────────────────────────────────   │
│                                                                 │
│  📏 Height & Weight                                 [ ○ OFF ]  │
│     Only doctors can see this information                      │
│                                                                 │
│  📋 Medical History                                 [ ○ OFF ]  │
│     Only doctors can see your full medical history             │
│                                                                 │
│  💳 Insurance Details                               [ ○ OFF ]  │
│     Only verified doctors can see insurance info               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Profile Access Log Enhancement

### 6.1 Current Implementation

The [`ProfileAccessLog`](profiles/models.py:371) model exists but needs enhanced `access_type` choices.

### 6.2 Recommended Updates

```python
# Add to ProfileAccessLog model - New access_type choices
access_type = models.CharField(
    max_length=25,
    choices=[
        ("emergency", "Emergency Scan"),
        ("emergency_alert", "Emergency Alert"),
        ("api", "API Access"),
        ("dashboard", "Dashboard View"),
        ("doctor_reveal", "Doctor Revealed All Data"),  # NEW
        ("doctor_login", "Doctor Login Attempt"),        # NEW
    ],
)
```

### 6.3 Log Entry Data Structure

```json
{
    "profile_id": "uuid-of-profile",
    "accessed_by": "doctor-user-id",
    "access_role": "doctor",
    "access_type": "doctor_reveal",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0...)",
    "accessed_at": "2026-03-16T10:30:00Z",
    "revealed_sections": [
        "medical_history",
        "medications_full",
        "physical_info",
        "insurance"
    ]
}
```

---

## 7. System Architecture Recommendations

### 7.1 Scalability Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐                                               │
│  │   CDN       │  Static assets, cached emergency views      │
│  │  (Cloudflare│                                               │
│  │   /AWS)     │                                               │
│  └──────┬──────┘                                               │
│         │                                                       │
│         ↓                                                       │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │  Load       │────▶│  Django      │────▶│  Database   │    │
│  │  Balancer   │     │  App Server  │     │  (PostgreSQL│    │
│  │             │     │  (Gunicorn)  │     │   Cluster)  │    │
│  └─────────────┘     └──────┬──────┘     └─────────────┘    │
│                             │                                   │
│                             ↓                                   │
│                    ┌───────────────┐                          │
│                    │   Redis Cache  │                          │
│                    │  (Session/     │                          │
│                    │   Rate Limit) │                          │
│                    └───────────────┘                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    SECURITY LAYER                           ││
│  │  • HTTPS/TLS 1.3                                           ││
│  │  • Rate limiting (30 req/min per IP)                       ││
│  │  • CSRF protection                                         ││
│  │  • Input validation                                        ││
│  │  • SQL injection prevention                                ││
│  │  • XSS protection                                           ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Mobile Optimization

| Optimization | Implementation |
|--------------|----------------|
| **Initial Load** | < 2 seconds on 3G |
| **Page Size** | < 100KB (excluding images) |
| **Critical CSS** | Inline above-the-fold content |
| **Lazy Loading** | Images below fold |
| **Service Worker** | Offline capability for saved profiles |
| **Touch Targets** | Minimum 44x44px |
| **Viewport** | Responsive, mobile-first |

### 7.3 Emergency Usability Features

```
┌─────────────────────────────────────────────────────────────────┐
│              EMERGENCY USABILITY REQUIREMENTS                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. ZERO-AUTH ACCESS                                            │
│     • QR/NFC scan → immediate emergency view                    │
│     • No login required for life-saving info                   │
│     • Works in airplane mode after first load                  │
│                                                                 │
│  2. HIGH-CONTRAST DESIGN                                        │
│     • WCAG AA compliant (4.5:1 contrast minimum)                │
│     • Dark mode support                                         │
│     • Large text option                                         │
│                                                                 │
│  3. OFFLINE CAPABILITY                                          │
│     • Service worker caches critical data                      │
│     • Works when cell service unavailable                      │
│     • Emergency contacts accessible offline                    │
│                                                                 │
│  4. ONE-TAP ACTIONS                                             │
│     • Send Emergency Alert - single tap                         │
│     • Call Contact - single tap                                 │
│     • Find Hospital - single tap                                │
│                                                                 │
│  5. MULTI-LANGUAGE SUPPORT                                      │
│     • Arabic (RTL)                                              │
│     • English                                                   │
│     • Auto-detect from device settings                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.4 Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DATA ENCRYPTION                                                │
│  ───────────────────────────────────────────────────────────   │
│                                                                 │
│  • At Rest: Fernet (Symmetric) for insurance images              │
│  • In Transit: TLS 1.3                                          │
│  • Database: Encrypted PostgreSQL volume                        │
│  • Backups: Encrypted with KMS                                  │
│                                                                 │
│  ACCESS CONTROL                                                 │
│  ───────────────────────────────────────────────────────────   │
│                                                                 │
│  Level 0: Public (No Auth)                                      │
│    → Emergency view (blood type, allergies, medications)       │
│                                                                 │
│  Level 1: Authenticated User                                    │
│    → Own profile management                                     │
│                                                                 │
│  Level 2: Verified Doctor                                       │
│    → Full medical history + insurance                           │
│    → Requires license number verification                       │
│                                                                 │
│  Level 3: Admin                                                 │
│    → All data + user management                                 │
│                                                                 │
│  RATE LIMITING                                                   │
│  ───────────────────────────────────────────────────────────   │
│                                                                 │
│  • Emergency scan API: 30 requests/minute/IP                   │
│  • Doctor reveal: 10 requests/minute/IP                         │
│  • Emergency alert: 5 requests/minute/IP                        │
│                                                                 │
│  AUDIT LOGGING                                                  │
│  ───────────────────────────────────────────────────────────   │
│                                                                 │
│  All access events logged:                                      │
│  • Timestamp                                                     │
│  • IP address                                                    │
│  • User agent                                                    │
│  • Access type                                                   │
│  • Data fields accessed                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Implementation Recommendations

### 8.1 Priority 1: Critical Fixes

1. **Add Emergency Notes visibility toggle** to `MedicalProfile` model
2. **Implement warning modal** for hiding critical fields
3. **Add "doctor_reveal" access type** to `ProfileAccessLog`

### 8.2 Priority 2: Doctor Expanded View

1. **Create "Reveal All Data" button** in emergency scan template
2. **Implement doctor authentication modal** with login form
3. **Add expanded view section** with animation effects

### 8.3 Priority 3: Enhanced Privacy UI

1. **Design privacy settings page** with clear explanations
2. **Add contextual help** for each visibility toggle
3. **Implement "undo" functionality** for privacy changes

### 8.4 Priority 4: Monitoring & Analytics

1. **Dashboard for access logs** (patient view)
2. **Doctor verification queue** (admin view)
3. **Privacy compliance reporting**

---

## 9. Summary

This design document provides a comprehensive visibility system for the SYRA emergency medical information application:

| Deliverable | Status |
|-------------|--------|
| ✅ Complete field list for Default Emergency View | Implemented in EmergencyProfileSerializer |
| ✅ Complete field list for Doctor Expanded View | Defined in this document |
| ✅ Recommended mandatory public fields | Blood type, severe allergies |
| ✅ UX design for "Reveal All Data" button | Detailed mockups and styling |
| ✅ Warning messages for hiding critical info | Designed with implementation guidance |
| ✅ System architecture for scalability/security | Documented with diagrams |

**Key Takeaways:**
- The existing codebase provides a solid foundation with visibility controls already implemented
- The main gaps are in the **UI flow for doctors** to reveal data and **warning messages** for critical field privacy
- Mandatory fields (blood type, severe allergies) should display warnings if patients try to hide them
- All expanded data access should be logged with the new "doctor_reveal" access type
