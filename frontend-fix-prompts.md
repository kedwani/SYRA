
review the every task before doing it  and give me a percntage how good is the task
do them task by task , 

### ISSUE-RTL-002: Flip Icons for RTL Mode

```
Implement icon flipping for RTL (Arabic) mode in the SYRA project.

Problem: Directional icons (arrows, chevrons) don't flip in RTL, causing confusion.

Task:
1. Add RTL flip utility to base.html:
```css
/* Add to custom styles section */
[dir="rtl"] .rtl-flip {
    transform: scaleX(-1);
}

/* Don't flip icons that shouldn't flip (like hearts, medical symbols) */
.rtl-no-flip {
    transform: none !important;
}
```

2. Identify directional icons to flip:
   - Left/right arrows
   - Chevrons
   - Navigation arrows
   - Back/forward buttons
   - Directional indicators

3. Add rtl-flip class:
```html
<!-- Before -->
<svg class="w-4 h-4">
    <path d="M11 16l-4-4m0 0l4-4"/>
</svg>

<!-- After -->
<svg class="w-4 h-4 rtl-flip">
    <path d="M11 16l-4-4m0 0l4-4"/>
</svg>
```

4. Icons that should NOT flip (add rtl-no-flip):
   - Hearts
   - Medical symbols (caduceus)
   - Circular icons
   - Symmetrical icons

5. Test in Arabic mode
6. Verify all directional icons flip correctly

Files to update:
- templates/base.html (add CSS)
- templates/profiles/emergency_scan.html
- templates/accounts/login.html
- All templates with directional icons
```
review the task before doing it and wait for my comfirmation and give me a percntage how good is the task



### ISSUE-WCAG-004: Fix Success Color Contrast

```
Fix insufficient color contrast for success messages on white background.

Current problem (base.html line 89):
```javascript
success: '#16a34a',
```
On white background: Contrast 3.4:1 (FAILS WCAG AA 4.5:1 for normal text)

Task:
1. Update Tailwind config in base.html:
```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                success: '#15803d',  // Darker green, 4.6:1 contrast
                // ... rest of colors
            }
        }
    }
}
```

2. Test all success messages:
   - Form submission confirmations
   - Success alerts
   - Status indicators

3. Verify contrast in both light and dark modes
4. Ensure success green is still visually distinct from other colors
5. Run accessibility audit

Test pages with success messages:
- Profile save confirmation
- Order success
- Contact saved
- Registration success
```

### ISSUE-WCAG-005: Improve Focus Indicator Contrast

```
Enhance keyboard focus indicators to meet WCAG requirements.

Current problem (base.html lines 280-287):
Focus outline may not have sufficient contrast against some backgrounds.

Task:
1. Update focus styles in base.html:
```css
/* Enhanced focus indicators with better contrast */
button:focus-visible,
a:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
    outline: 3px solid #1d4ed8;  /* Darker blue, better contrast */
    outline-offset: 2px;
}

/* Dark mode focus indicators */
.dark button:focus-visible,
.dark a:focus-visible,
.dark input:focus-visible,
.dark select:focus-visible,
.dark textarea:focus-visible {
    outline: 3px solid #60a5fa;  /* Light blue for dark backgrounds */
    outline-offset: 2px;
}

/* Extra high contrast for emergency buttons */
.btn-emergency:focus-visible {
    outline: 4px solid #fbbf24;  /* Yellow for maximum visibility */
    outline-offset: 2px;
}
```

2. Test keyboard navigation:
   - Tab through all interactive elements
   - Verify focus indicator is visible on all backgrounds
   - Check in both light and dark modes

3. Ensure focus indicators meet WCAG 2.2 requirements:
   - Minimum 3:1 contrast ratio against background
   - Clearly visible
   - Consistent style

4. Test with keyboard users

Files to update:
- templates/base.html
```

### ISSUE-WCAG-006: Fix Red Gradient Header Contrast

```
Fix insufficient text contrast on red gradient background in emergency scan header.

Problem (emergency_scan.html line 204):
```html
<p class="text-red-100 dark:text-red-300 text-xs">SYRA • Smart Medical ID</p>
```
On gradient background from-red-600 to-red-800:
- Light mode: Contrast 1.9:1 (FAILS)
- Dark mode: Contrast 2.8:1 (FAILS)

Task:
1. Update template (templates/profiles/emergency_scan.html):
```html
<!-- Before -->
<p class="text-red-100 dark:text-red-300 text-xs">SYRA • Smart Medical ID</p>

<!-- After -->
<p class="text-white text-xs opacity-90">SYRA • Smart Medical ID</p>
```

2. Test contrast in both modes:
   - Light mode: white on red-600 = 4.9:1 (PASS)
   - Dark mode: white on red-900 = 9.2:1 (PASS)

3. Verify readability of:
   - Main title
   - Subtitle
   - Last updated date
   - All text on gradient backgrounds

4. Apply same fix to any other gradient backgrounds

Files to update:
- templates/profiles/emergency_scan.html
```

### ISSUE-WCAG-009: Add Skip Navigation Link

```
Add "skip to main content" link for keyboard users.

Task:
1. Add skip link to base.html (before navigation):
```html
<!-- Add after <body> tag, before navigation -->
<a href="#main-content" 
   class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow-lg transition-all">
    {% trans "Skip to main content" %}
</a>
```

2. Add sr-only utility if not present:
```css
/* Screen reader only - visible only when focused */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}

.focus\:not-sr-only:focus {
    position: static;
    width: auto;
    height: auto;
    padding: 0.5rem 1rem;
    margin: 0;
    overflow: visible;
    clip: auto;
    white-space: normal;
}
```

3. Add ID to main content area:
```html
{% block content %}
<main id="main-content" class="...">
    <!-- content -->
</main>
{% endblock %}
```

4. Add translations:
```python
# In django.po
msgid "Skip to main content"
msgstr "تخطي إلى المحتوى الرئيسي"
```

5. Test keyboard navigation:
   - Press Tab as first action on page
   - Skip link should appear
   - Press Enter
   - Focus should jump to main content

Files to update:
- templates/base.html
```

### ISSUE-CONTENT-001: Remove Duplicate "Protected" Messages

```
Reduce redundant "Protected" messages on emergency scan page.

Current problem: The same protection message is repeated in every protected section.

Task:
1. Add single prominent notice at top (templates/profiles/emergency_scan.html):
```html
<!-- Add after emergency action buttons, before sections -->
{% if not user_role == 'doctor' and not user_role == 'admin' and not is_profile_owner %}
<div class="px-3 mb-4">
    <div class="bg-blue-50 dark:bg-blue-900/30 border-l-4 border-blue-500 rounded-lg p-3">
        <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
            <p class="text-sm font-medium text-blue-900 dark:text-blue-100">
                {% trans "Some sections are protected and require doctor authorization to view." %}
            </p>
        </div>
        <a href="{% url 'login' %}?next={{ request.path }}" 
           class="inline-flex items-center gap-1 mt-2 text-sm text-blue-600 dark:text-blue-400 hover:underline">
            {% trans "Sign in as verified doctor" %}
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
            </svg>
        </a>
    </div>
</div>
{% endif %}
```

2. Simplify protected sections to show only lock icon:
```html
<!-- Before: Verbose protection message -->
<div class="bg-white/20 rounded-lg p-3">
    <div class="flex items-center justify-center gap-1 mb-1">
        <svg class="w-4 h-4 text-white">...</svg>
        <p class="text-white text-xs font-medium">{% trans "Protected" %}</p>
    </div>
    <p class="text-white/80 text-xs mb-2">{% trans "Doctor authorization required" %}</p>
    <!-- Login button -->
</div>

<!-- After: Simple lock icon -->
<div class="bg-white/20 rounded-lg p-3 flex items-center justify-center">
    <svg class="w-8 h-8 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
    </svg>
</div>
```

3. Test with users to verify clarity is maintained
4. Ensure protected data security is not compromised

Files to update:
- templates/profiles/emergency_scan.html
```

### ISSUE-CONTENT-004: Improve Button Text Clarity

```
Improve clarity and conciseness of button text throughout the application.

Problem (emergency_scan.html line 238):
"Login as Doctor to View Protected Data" - Too long, unclear

Task:
1. Update button text in templates/profiles/emergency_scan.html:
```html
<!-- Before -->
<a href="..." class="...">
    {% trans "Login as Doctor to View Protected Data" %}
</a>

<!-- After -->
<a href="..." class="...">
    <span class="font-bold">{% trans "Doctor Login" %}</span>
    <span class="text-xs block mt-0.5 opacity-90">{% trans "Access full medical records" %}</span>
</a>
```

2. Review all buttons for clarity:
```bash
grep -r "{% trans.*button\|btn.*%}" templates/
```

3. Apply button text guidelines:
   - Maximum 3 words for primary action
   - Use verb + noun (e.g., "Save Profile", "Send Alert")
   - Add helper text below if explanation needed
   - Be specific, not generic ("Send Alert" not "Submit")

4. Update translations in django.po

Common button improvements:
- "Submit" → "Save Changes"
- "Click here" → "View Details"
- "Login as Doctor to View Protected Data" → "Doctor Login"
- "Show Protected Data" → "Show Full Record"

Files to update:
- templates/profiles/emergency_scan.html
- All templates with buttons
```

### ISSUE-CONTENT-005: Standardize Protection Terminology

```
Standardize the terminology used for protected/restricted medical data.

Problem: Inconsistent use of:
- "Show Protected Data"
- "Reveal Additional Data"  
- "Access Protected Information"
- "View Full Record"

Task:
1. Choose consistent terminology:
   - For buttons: "View Full Medical Record"
   - For status: "Protected Information"
   - For explanations: "Doctor authorization required"

2. Update all instances in templates:
```bash
grep -r "Protected\|Reveal\|Additional Data" templates/
```

3. Update django.po:
```python
# Remove/consolidate:
msgid "Show Protected Data"
msgid "Reveal Additional Data"
msgid "Hide Additional Data"

# Standardize to:
msgid "View Full Medical Record"
msgstr "عرض السجل الطبي الكامل"

msgid "Hide Medical Details"
msgstr "إخفاء التفاصيل الطبية"

msgid "Protected Information"
msgstr "معلومات محمية"
```

4. Document terminology in style guide

Files to update:
- templates/profiles/emergency_scan.html
- locale/ar/LC_MESSAGES/django.po
- Create: docs/terminology-guide.md
```

### ISSUE-UX-001: Standardize Card Styling

```
Create consistent card styling system for the SYRA project.

Problem: Different sections use different card styles without clear hierarchy.

Task:
1. Define card component classes in base.html:
```css
/* Add to custom styles section */

/* Card system - consistent styling */
.card-emergency {
    /* For critical, life-saving information */
    background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
    color: white;
    padding: 1rem;
    border-radius: 0.75rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-warning {
    /* For important warnings (allergies, conditions) */
    background: white;
    border: 2px solid #f59e0b;
    border-left-width: 4px;
    padding: 1rem;
    border-radius: 0.75rem;
}

.dark .card-warning {
    background: #451a03;
    border-color: #f59e0b;
}

.card-info {
    /* For general medical information */
    background: white;
    border: 1px solid #e5e7eb;
    padding: 1rem;
    border-radius: 0.75rem;
}

.dark .card-info {
    background: #262626;
    border-color: #404040;
}

.card-protected {
    /* For protected/locked sections */
    background: rgba(0, 0, 0, 0.05);
    border: 2px dashed #9ca3af;
    padding: 1rem;
    border-radius: 0.75rem;
}

.dark .card-protected {
    background: rgba(255, 255, 255, 0.05);
    border-color: #525252;
}
```

2. Apply consistent classes in emergency_scan.html:
```html
<!-- Blood type: Emergency card -->
<div class="card-emergency">
    <!-- content -->
</div>

<!-- Allergies: Warning card -->
<div class="card-warning">
    <!-- content -->
</div>

<!-- Medications: Info card -->
<div class="card-info">
    <!-- content -->
</div>

<!-- Protected data: Protected card -->
<div class="card-protected">
    <!-- content -->
</div>
```

3. Document card system in style guide
4. Update all templates to use card classes
5. Test in both light and dark modes

Files to update:
- templates/base.html (add CSS)
- templates/profiles/emergency_scan.html
- Create: docs/ui-style-guide.md
```

### ISSUE-UX-006: Fix Dark Mode Background Consistency

```
Standardize dark mode background colors for consistent appearance.

Problem (base.html): Too many dark gray shades used inconsistently.

Task:
1. Define semantic background levels in base.html:
```css
/* Dark mode semantic backgrounds */
.dark {
    /* Level 0: App background */
    --bg-0: #0a0a0a;
    
    /* Level 1: Card background */
    --bg-1: #171717;
    
    /* Level 2: Elevated elements */
    --bg-2: #262626;
    
    /* Level 3: Highest elevation */
    --bg-3: #404040;
}

/* Apply semantic colors */
.dark body {
    background-color: var(--bg-0);
}

.dark .bg-white {
    background-color: var(--bg-1);
}

.dark .bg-gray-50,
.dark .bg-gray-100 {
    background-color: var(--bg-1);
}

.dark .bg-gray-200 {
    background-color: var(--bg-2);
}

.dark nav,
.dark header,
.dark footer {
    background-color: var(--bg-2);
}
```

2. Update all templates to use semantic levels:
   - Page background: Level 0
   - Cards/containers: Level 1
   - Navigation/headers: Level 2
   - Modals/popovers: Level 3

3. Remove custom one-off dark shades (#1f1f1f, etc.)

4. Test all pages in dark mode
5. Verify visual hierarchy is clear

Files to update:
- templates/base.html
```

### ISSUE-UX-007: Standardize Dark Mode Border Colors

```
Ensure all borders have appropriate dark mode variants.

Task:
1. Add dark mode borders to all border classes:
```bash
# Find all borders without dark mode variants
grep -r "border-\(red\|blue\|green\|gray\)-[0-9]" templates/ | grep -v "dark:border"
```

2. Apply standard dark mode border pattern:
```html
<!-- Before -->
<div class="border-2 border-red-200">

<!-- After -->
<div class="border-2 border-red-200 dark:border-red-800">
```

3. Border color mapping for dark mode:
   - Light 100-300 → Dark 700-900
   - Example: border-gray-200 → dark:border-gray-700
   - Example: border-blue-300 → dark:border-blue-700

4. Create utility class helper:
```css
/* Add to base.html */
.border-adaptive {
    border-color: #e5e7eb; /* gray-200 */
}

.dark .border-adaptive {
    border-color: #404040; /* gray-700 */
}
```

5. Test all bordered elements in dark mode

Files to update:
- All template files with borders
```

### ISSUE-PERF-001: Optimize Font Loading

```
Optimize Google Fonts loading for better performance.

Current problem (base.html lines 64-67): Non-optimized font loading.

Task:
1. Add preconnect to base.html (before font links):
```html
<!-- Preconnect to font CDNs -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

2. Preload critical fonts:
```html
<!-- Preload Inter (critical for initial render) -->
<link rel="preload" 
      as="font" 
      href="https://fonts.gstatic.com/s/inter/v12/UcC73FwrK3iLTeHuS_fvQtMwCp50KnMa1ZL7W0Q5nw.woff2"
      type="font/woff2"
      crossorigin>

<!-- Load fonts with display=swap for better performance -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap" rel="stylesheet">
```

3. Optional: Self-host fonts for better control:
```bash
# Download fonts to static/fonts/
# Update base.html with @font-face declarations
```

4. Measure improvement with Lighthouse

Expected improvement: 0.5-1s faster first contentful paint

Files to update:
- templates/base.html
```

---

## 🔵 LOW PRIORITY FIXES

### ISSUE-AR-004: Add Context to Short Translations

```
Add context to ambiguous short translations using msgctxt.

Task:
1. Update django.po to add context:
```python
# Before
msgid "Notes"
msgstr "ملاحظات"

# After
msgctxt "medical notes"
msgid "Notes"
msgstr "الملاحظات الطبية"

msgctxt "general notes"
msgid "Notes"
msgstr "ملاحظات"

# For "Create" button
msgctxt "create profile"
msgid "Create"
msgstr "إنشاء ملف"

msgctxt "create account"
msgid "Create"
msgstr "إنشاء حساب"
```

2. Update template usage:
```django
{% load i18n %}

<!-- Add context -->
{% trans "Notes" context "medical notes" %}
{% trans "Create" context "create profile" %}
```

3. Recompile translations:
```bash
python manage.py makemessages -l ar
python manage.py compilemessages
```

Files to update:
- locale/ar/LC_MESSAGES/django.po
- Templates using ambiguous short strings
```

### ISSUE-AR-006: Localize Phone Number Placeholders

```
Adapt phone number placeholders for Arabic users.

Current: "01xxxxxxxxx" (not localized)

Task:
1. Update django.po:
```python
msgid "01xxxxxxxxx"
msgstr "٠١xxxxxxxxx"  # Arabic-Indic numerals
# Or with example:
msgstr "01xxxxxxxxx (مثال: 01012345678)"
```

2. Alternative: Use locale-aware placeholder:
```html
{% if LANGUAGE_CODE == 'ar' %}
    <input placeholder="٠١٢٣٤٥٦٧٨٩٠ (مثال)">
{% else %}
    <input placeholder="01234567890 (example)">
{% endif %}
```

3. Update all phone number inputs

Files to update:
- locale/ar/LC_MESSAGES/django.po
- templates/profiles/contact_form.html
- templates/store/checkout.html
```

### ISSUE-RTL-003: Fix Accordion Icons for RTL

```
Make accordion collapse/expand icons RTL-aware.

Task:
1. Update accordion JavaScript (emergency_scan.html line 185):
```javascript
// Before
icon.classList.toggle('rotate-180');

// After - RTL-aware rotation
const isRTL = document.documentElement.dir === 'rtl';
if (isRTL) {
    icon.classList.toggle('rotate-180-rtl');
} else {
    icon.classList.toggle('rotate-180');
}
```

2. Add RTL rotation class:
```css
/* In base.html */
.rotate-180-rtl {
    transform: rotate(180deg) scaleX(-1);
}
```

3. Test accordion in both LTR and RTL modes

Files to update:
- templates/profiles/emergency_scan.html
- templates/base.html
```

### ISSUE-RTL-004: Optimize Arabic Font Loading

```
Improve Arabic font (Cairo) loading performance.

Task:
1. Preload Cairo font in base.html:
```html
<link rel="preload" 
      as="style" 
      href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap">
```

2. Consider using Cairo variable font:
```html
<!-- Variable font is smaller file size -->
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@200..900&display=swap" rel="stylesheet">
```

3. Or self-host Cairo font:
```css
@font-face {
    font-family: 'Cairo';
    src: url('/static/fonts/cairo-variable.woff2') format('woff2-variations');
    font-weight: 200 900;
    font-display: swap;
}
```

4. Measure loading time improvement

Files to update:
- templates/base.html
```

### ISSUE-WCAG-007: Improve Protected Data Icon Contrast

```
Increase contrast for lock icons on protected data sections.

Problem: White icons on semi-transparent white background (emergency_scan.html lines 323-327).

Task:
1. Increase background opacity:
```html
<!-- Before -->
<div class="bg-white/20 rounded-lg p-3">
    <svg class="w-4 h-4 text-white">...</svg>
</div>

<!-- After -->
<div class="bg-white/30 rounded-lg p-3">
    <svg class="w-4 h-4 text-white drop-shadow-lg">...</svg>
</div>
```

2. Or use solid background with proper contrast:
```html
<div class="bg-gray-700/90 rounded-lg p-3">
    <svg class="w-4 h-4 text-white">...</svg>
</div>
```

3. Test visibility in both light and dark modes

Files to update:
- templates/profiles/emergency_scan.html
```

### ISSUE-CONTENT-002: Simplify Emergency Context Messages

```
Remove redundant explanatory text in emergency context.

Problem (emergency_scan.html line 147): 
"This person will be contacted first in emergencies" - shown ON emergency page.

Task:
1. Simplify helper text:
```html
<!-- Before -->
<p class="text-xs text-gray-500">
    {% trans "This person will be contacted first in emergencies" %}
</p>

<!-- After -->
<span class="text-xs text-gray-500">
    {% trans "Primary" %}
</span>
```

2. Or use icon instead of text:
```html
<span class="inline-flex items-center gap-1 text-xs text-gray-500">
    <svg class="w-3 h-3" fill="currentColor">
        <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z"/>
    </svg>
    {% trans "Primary" %}
</span>
```

3. Update translations

Files to update:
- templates/profiles/emergency_scan.html
- locale/ar/LC_MESSAGES/django.po
```

### ISSUE-CONTENT-003: Streamline Empty State Messages

```
Simplify repetitive "No X listed" messages.

Task:
1. Create reusable empty state component:
```html
<!-- Create: templates/partials/empty_state.html -->
{% load i18n %}
<div class="text-center py-4">
    <svg class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-2" 
         fill="none" stroke="currentColor" viewBox="0 0 24 24">
        {{ icon_path|safe }}
    </svg>
    <p class="text-sm text-gray-500 dark:text-gray-400">
        {{ message }}
    </p>
</div>
```

2. Use in templates:
```django
{% if not profile.allergies %}
    {% include 'partials/empty_state.html' with message="None listed" icon_path="..." %}
{% endif %}
```

3. Standardize all empty states

Files to update:
- Create: templates/partials/empty_state.html
- templates/profiles/emergency_scan.html
```

### ISSUE-CONTENT-007: Reorder Emergency Page Content

```
Improve information hierarchy on emergency scan page.

Current problem: Action buttons appear before medical information.

Task:
1. Reorder emergency_scan.html sections:
```
NEW ORDER:
1. Header with user info
2. CRITICAL INFORMATION (always visible):
   - Blood type (large, prominent)
   - Allergies (if any, warning style)
   - Primary emergency contact
3. ACTION BUTTONS:
   - Emergency Alert
   - Nearby Hospitals
4. IMPORTANT INFORMATION:
   - Chronic diseases
   - Current medications
   - Emergency notes
5. DETAILED INFORMATION (accordion):
   - Secondary emergency contact
   - Physical data
   - Medical history
   - Insurance
```

2. Implement visual hierarchy:
```html
<!-- Priority 1: Large, gradient background -->
<section class="priority-1 bg-gradient-to-br from-red-600 to-red-800 text-white p-6 rounded-xl mb-4">
    <!-- Blood type -->
</section>

<!-- Priority 2: Warning borders -->
<section class="priority-2 border-l-4 border-orange-500 bg-orange-50 p-4 rounded-lg mb-4">
    <!-- Allergies -->
</section>

<!-- Action buttons -->
<section class="actions grid grid-cols-2 gap-3 mb-6">
    <!-- Buttons -->
</section>

<!-- Priority 3: Regular cards -->
<section class="priority-3 space-y-3">
    <!-- Other info -->
</section>
```

3. Test with users for usability

Files to update:
- templates/profiles/emergency_scan.html
```

### ISSUE-CONTENT-008: Implement Visual Information Hierarchy

```
Create clear visual hierarchy for emergency medical information.

Task:
1. Define hierarchy levels in CSS (base.html):
```css
/* Information priority levels */
.priority-critical {
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1.2;
}

.priority-high {
    font-size: 1.25rem;
    font-weight: 600;
    line-height: 1.3;
}

.priority-medium {
    font-size: 1rem;
    font-weight: 500;
    line-height: 1.5;
}

.priority-low {
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1.6;
}
```

2. Apply to emergency_scan.html:
```html
<!-- Critical: Blood type -->
<p class="priority-critical">{{ profile.blood_type }}</p>

<!-- High: Allergies, chronic diseases -->
<h3 class="priority-high">{% trans "Allergies" %}</h3>

<!-- Medium: Medications, contacts -->
<h4 class="priority-medium">{% trans "Current Medications" %}</h4>

<!-- Low: Details, notes -->
<p class="priority-low">{{ item.notes }}</p>
```

3. Add color coding:
```css
.info-emergency { color: #dc2626; }  /* Red */
.info-warning { color: #f59e0b; }    /* Orange */
.info-normal { color: #3b82f6; }     /* Blue */
.info-neutral { color: #6b7280; }    /* Gray */
```

Files to update:
- templates/base.html
- templates/profiles/emergency_scan.html
```

### ISSUE-UX-002: Define Button Component System

```
Create consistent button styling system.

Task:
1. Define button classes in base.html:
```css
/* Button system */
.btn {
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-weight: 600;
    transition: all 0.2s;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.btn-primary {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn-emergency {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
}

.btn-emergency:hover {
    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
}

.btn-secondary {
    background: white;
    color: #374151;
    border: 2px solid #e5e7eb;
}

.dark .btn-secondary {
    background: #262626;
    color: #f3f4f6;
    border-color: #404040;
}

.btn-ghost {
    background: transparent;
    color: #3b82f6;
}

.btn-ghost:hover {
    background: rgba(59, 130, 246, 0.1);
}

/* Button sizes */
.btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
}

.btn-lg {
    padding: 0.75rem 1.5rem;
    font-size: 1.125rem;
}
```

2. Update all buttons to use classes:
```html
<button class="btn btn-primary">
    {% trans "Save" %}
</button>

<button class="btn btn-emergency">
    {% trans "Emergency Alert" %}
</button>
```

3. Document button system in style guide

Files to update:
- templates/base.html
- All templates with buttons
```

### ISSUE-UX-003: Standardize Icon Sizes

```
Create consistent icon sizing system.

Task:
1. Define icon size utilities (base.html):
```css
/* Icon sizing system */
.icon-xs { width: 12px; height: 12px; }  /* Inline small */
.icon-sm { width: 16px; height: 16px; }  /* Inline text */
.icon-md { width: 20px; height: 20px; }  /* Buttons */
.icon-lg { width: 24px; height: 24px; }  /* Headers */
.icon-xl { width: 32px; height: 32px; }  /* Section headers */
.icon-2xl { width: 48px; height: 48px; } /* Hero/Feature */
```

2. Replace Tailwind w-* h-* with semantic classes:
```html
<!-- Before -->
<svg class="w-4 h-4">...</svg>

<!-- After -->
<svg class="icon-sm">...</svg>
```

3. Create icon usage guidelines:
- XS (12px): Inline indicators, badges
- SM (16px): Inline with text
- MD (20px): Buttons, controls
- LG (24px): Section headers
- XL (32px): Major sections
- 2XL (48px): Hero sections

4. Update all icons consistently

Files to update:
- templates/base.html
- All templates with SVG icons
```

### ISSUE-UX-004: Standardize Card Padding

```
Use consistent padding values for cards.

Task:
1. Define card padding scale:
```css
.card-sm { padding: 0.75rem; }   /* Small cards */
.card-md { padding: 1rem; }      /* Default cards */
.card-lg { padding: 1.5rem; }    /* Large cards */
```

2. Replace arbitrary padding:
```html
<!-- Before -->
<div class="p-3">
<div class="p-4">
<div class="p-5">

<!-- After -->
<div class="card-sm">
<div class="card-md">
<div class="card-lg">
```

3. Update all cards

Files to update:
- templates/base.html
- templates/profiles/emergency_scan.html
```

### ISSUE-UX-005: Standardize Grid Gaps

```
Use consistent gap sizing in grid layouts.

Task:
1. Define grid gap scale:
```css
.gap-cards { gap: 0.75rem; }  /* Between cards */
.gap-sections { gap: 1rem; }  /* Between sections */
.gap-groups { gap: 1.5rem; }  /* Between groups */
```

2. Apply consistently:
```html
<div class="grid grid-cols-2 gap-cards">
```

3. Update all grids

Files to update:
- All templates with grid layouts
```

### ISSUE-DARK-001: Add Visual Dark Mode Toggle

```
Add clear dark mode toggle button.

Task:
1. Add toggle button to base.html navigation:
```html
<button id="dark-mode-toggle" 
        aria-label="{% trans 'Toggle dark mode' %}"
        class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
    <!-- Sun icon (visible in dark mode) -->
    <svg class="w-5 h-5 hidden dark:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
    </svg>
    <!-- Moon icon (visible in light mode) -->
    <svg class="w-5 h-5 block dark:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
    </svg>
</button>

<script>
document.getElementById('dark-mode-toggle').addEventListener('click', function() {
    document.documentElement.classList.toggle('dark');
    const isDark = document.documentElement.classList.contains('dark');
    localStorage.setItem('syra-dark-mode', isDark);
});
</script>
```

2. Add accessibility announcement:
```javascript
// Announce to screen readers
const announcement = isDark ? 
    gettext('Dark mode enabled') : 
    gettext('Light mode enabled');
// Use ARIA live region for announcement
```

3. Add translations for toggle

Files to update:
- templates/base.html
```

### ISSUE-DARK-003: Enhance Dark Mode Color Differentiation

```
Improve distinction between UI states in dark mode.

Task:
1. Add pronounced hover/active states:
```css
/* Dark mode interactive states */
.dark button:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

.dark button:active {
    background-color: rgba(255, 255, 255, 0.15);
    transform: scale(0.98);
}

.dark button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.dark a:hover {
    background-color: rgba(59, 130, 246, 0.1);
}
```

2. Test all interactive elements in dark mode
3. Verify clear visual feedback

Files to update:
- templates/base.html
```

### ISSUE-PERF-002: Optimize Event Listeners

```
Use event delegation for better performance.

Task:
1. Update emergency_scan.html (lines 176-187):
```javascript
// Before: Individual listeners
accordionHeaders.forEach(header => {
    header.addEventListener('click', function() {
        // Handle click
    });
});

// After: Event delegation
document.addEventListener('click', function(e) {
    // Check if clicked element is an accordion header
    const header = e.target.closest('.accordion-header');
    if (!header) return;
    
    const accordion = header.closest('.accordion-item');
    const content = accordion.querySelector('.accordion-content');
    const icon = header.querySelector('.accordion-icon');
    
    content.classList.toggle('hidden');
    icon.classList.toggle('rotate-180');
});
```

2. Apply to other event listeners
3. Test functionality

Files to update:
- templates/profiles/emergency_scan.html
```

---

## Testing Checklist

After applying fixes, run these tests:

### Automated Tests
```bash
# Accessibility audit
npm run test:a11y

# Color contrast check
npm run test:contrast

# Translation coverage
python manage.py makemessages --all
# Check for untranslated strings
```
