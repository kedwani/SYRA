"""
Medical Data Library for autocomplete suggestions.
Contains common medications and diagnoses for Egypt/Middle East region.
"""

# Common Medications (English)
MEDICATIONS_EN = [
    # Pain Relief
    "Paracetamol (Acetaminophen)",
    "Ibuprofen",
    "Diclofenac",
    "Tramadol",
    "Morphine",
    "Codeine",
    "Aspirin",
    "Naproxen",
    "Pethidine",
    "Ketorolac",
    # Antibiotics
    "Amoxicillin",
    "Azithromycin",
    "Ciprofloxacin",
    "Ceftriaxone",
    "Metronidazole",
    "Doxycycline",
    "Cephalexin",
    "Levofloxacin",
    "Augmentin (Amoxicillin/Clavulanic Acid)",
    "Nitrofurantoin",
    # Cardiovascular
    "Amlodipine",
    "Metoprolol",
    "Atenolol",
    "Losartan",
    "Enalapril",
    "Ramipril",
    "Captopril",
    "Hydrochlorothiazide",
    "Furosemide",
    "Spironolactone",
    "Digoxin",
    "Warfarin",
    "Aspirin (Cardio)",
    "Clopidogrel",
    "Atorvastatin",
    "Rosuvastatin",
    "Simvastatin",
    # Diabetes
    "Metformin",
    "Gliclazide",
    "Glimepiride",
    "Insulin Glargine",
    "Insulin Regular",
    "Insulin Lispro",
    "Sitagliptin",
    "Empagliflozin",
    # Respiratory
    "Salbutamol",
    "Budesonide",
    "Montelukast",
    "Theophylline",
    "Prednisone",
    "Fluticasone",
    "Ipratropium",
    # Gastrointestinal
    "Omeprazole",
    "Pantoprazole",
    "Ranitidine",
    "Famotidine",
    "Metoclopramide",
    "Domperidone",
    "Loperamide",
    "Sennosides",
    "Lactulose",
    "Mesalazine",
    # Neurological
    "Carbamazepine",
    "Phenytoin",
    "Sodium Valproate",
    "Levodopa",
    "Piracetam",
    "Cinnarizine",
    "Pregabalin",
    "Gabapentin",
    "Amitriptyline",
    "Fluoxetine",
    "Sertraline",
    "Escitalopram",
    # Psychiatric
    "Haloperidol",
    "Risperidone",
    "Olanzapine",
    "Quetiapine",
    "Diazepam",
    "Clonazepam",
    "Lorazepam",
    "Alprazolam",
    "Chlorpromazine",
    # Thyroid
    "Levothyroxine",
    "Carbimazole",
    "Propylthiouracil",
    # Musculoskeletal
    "Cyclobenzaprine",
    "Baclofen",
    "Tizanidine",
    "Methocarbamol",
    # Vitamins & Supplements
    "Vitamin D3",
    "Vitamin B12",
    "Ferrous Sulfate (Iron)",
    "Folic Acid",
    "Calcium Carbonate",
    "Magnesium Sulfate",
    "Zinc",
    # Anticoagulants
    "Enoxaparin",
    "Heparin",
    "Rivaroxaban",
    "Apixaban",
    # Others
    "Allopurinol",
    "Colchicine",
    "Rasburicase",
    "Methylprednisolone",
    "Dexamethasone",
    "Hydrocortisone",
    "Normal Saline",
    "Dextrose 5%",
    "Ringer's Solution",
]

# Common Medications (Arabic)
MEDICATIONS_AR = [
    # مسكنات الألم
    "باراسيتامول (أسيتأمينوفين)",
    "إيبوبروفين",
    "ديكلوفيناك",
    "ترامادول",
    "مورفين",
    "كودايين",
    "أسبرين",
    "نابروكسين",
    "بيثيدين",
    "كيتورولاك",
    # المضادات الحيوية
    "أموكسيسيلين",
    "أزيثرومايسين",
    "سيبروفلوكساسين",
    "سيفترياكسون",
    "ميترونيدازول",
    "دوكسي سيكلين",
    "سيفالكسين",
    "ليفوفلوكساسين",
    "أوجمنتين (أموكسيسيلين/حمض كلافولانيك)",
    "نيتروفورانتوين",
    # أمراض القلب والأوعية الدموية
    "أملوديبين",
    "ميتوبrolول",
    "أتينولول",
    "لوسارتان",
    "إينالابريل",
    "راميبريل",
    "كابتوبريل",
    "هيدروكلوروثيازيد",
    "فوروسيميد",
    "سبيرونولاكتون",
    "ديجوكسين",
    "وارفارين",
    "أسبرين (قلبي)",
    "كلوبيدوجريل",
    "أتورفاستاتين",
    "روسوفاستاتين",
    "سيفاستاتين",
    # السكر
    "ميتفورمين",
    "غليكلازيد",
    "غليمبيريد",
    "أنسولين غلارجين",
    "أنسولين عادي",
    "أنسولين ليسبرو",
    "سيتاغليبتين",
    "إمباغليفلوزين",
    # الجهاز التنفسي
    "سالبوتامول",
    "بوديزونيد",
    "مونتيلوكاست",
    "ثيوفيلين",
    "بريدنيزون",
    "فلوتيكازون",
    "إبراتروبيوم",
    # الجهاز الهضمي
    "أوميبرازول",
    "بانتوبرازول",
    "رانيتيدين",
    "فاموتيدين",
    "ميتكلوبراميد",
    "دومبيريدون",
    "لوبيراميد",
    "سينوسايدس",
    "لاكتولوز",
    "ميزالازين",
    # الأعصاب
    "كاربامازيبين",
    "فينيتوين",
    "صوديوم فالبروات",
    "ليفودوبا",
    "بيراسيتام",
    "سيناريزين",
    "بريغابالين",
    "جابابنتين",
    "أميتريبتيلين",
    "فلوكسيتين",
    "سيرترالين",
    "إس سيتالوبرام",
    # النفسية
    "هالوبيريدول",
    "رسبيريدون",
    "أولانزبين",
    "كويتيابين",
    "ديازيبام",
    "كلونازيبام",
    "لورازيبام",
    "ألبرازولام",
    "كلوربرومازين",
    # الغدة الدرقية
    "ليفوثيروكسين",
    "كاربيمازول",
    "بريد يوراسيل",
    # العضلات والعظام
    "سيكلوبنزامين",
    "باكلوفين",
    "تيزانيدين",
    "ميثوكاربامول",
    # الفيتamines والمكملات
    "فيتامين د3",
    "فيتامين ب12",
    "حديد (سلفات)",
    "حمض الفوليك",
    "كربونات الكالسيوم",
    "ماغنسيوم سلفات",
    "زنك",
    # مضادات التجلط
    "إينوكسابارين",
    "هيبارين",
    "ريفاروكسابان",
    "أبيكسابان",
    # أخرى
    "ألوبورينول",
    "كولشيسين",
    "راسيبوروكيز",
    "ميثيل بريدنيزولون",
    "ديكساميثازون",
    "هيدروكورتيزون",
    "محلول ملحي عادي",
    "جلوكوز 5%",
    "محلول رينغر",
]

# Common Diagnoses/Conditions (English)
DIAGNOSES_EN = [
    # Cardiovascular
    "Hypertension",
    "Diabetes Mellitus Type 2",
    "Coronary Artery Disease",
    "Heart Failure",
    "Atrial Fibrillation",
    "Arrhythmia",
    "Angina Pectoris",
    "Myocardial Infarction",
    "Valvular Heart Disease",
    "Peripheral Artery Disease",
    # Respiratory
    "Asthma",
    "COPD",
    "Bronchitis",
    "Pneumonia",
    "Pulmonary Embolism",
    "Tuberculosis",
    "Sleep Apnea",
    # Gastrointestinal
    "GERD",
    "Peptic Ulcer",
    "Gastritis",
    "Hepatitis",
    "Cirrhosis",
    "Pancreatitis",
    "IBD (Crohn's/Ulcerative Colitis)",
    "Gallstones",
    # Neurological
    "Epilepsy",
    "Migraine",
    "Parkinson's Disease",
    "Alzheimer's Disease",
    "Multiple Sclerosis",
    "Peripheral Neuropathy",
    "Stroke",
    # Psychiatric
    "Depression",
    "Anxiety Disorder",
    "Bipolar Disorder",
    "Schizophrenia",
    "OCD",
    "Insomnia",
    # Endocrine
    "Hypothyroidism",
    "Hyperthyroidism",
    "Cushing's Syndrome",
    "Addison's Disease",
    # Musculoskeletal
    "Osteoarthritis",
    "Rheumatoid Arthritis",
    "Osteoporosis",
    "Back Pain",
    "Gout",
    # Renal
    "Chronic Kidney Disease",
    "Kidney Stones",
    "Urinary Tract Infection",
    # Hematology
    "Anemia",
    "Sickle Cell Disease",
    "Thalassemia",
    "Leukemia",
    "Lymphoma",
    # Oncology
    "Breast Cancer",
    "Lung Cancer",
    "Colorectal Cancer",
    "Liver Cancer",
    "Prostate Cancer",
    # Autoimmune
    "Systemic Lupus Erythematosus",
    "Rheumatoid Arthritis",
    "Scleroderma",
    "Psoriasis",
    # Allergies
    "Drug Allergy",
    "Food Allergy",
    "Latex Allergy",
    "Penicillin Allergy",
    "Sulfa Drug Allergy",
    # Other Common Conditions
    "Hypothyroidism",
    "Hyperlipidemia",
    "Benign Prostatic Hyperplasia",
    "Glaucoma",
    "Cataract",
    "Chronic Pain",
    "Sleep Disorder",
]

# Common Diagnoses/Conditions (Arabic)
DIAGNOSES_AR = [
    # القلب والأوعية الدموية
    "ارتفاع ضغط الدم",
    "السكري النوع الثاني",
    "مرض الشريان التاجي",
    "قصور القلب",
    "الرجفان الأذيني",
    "اضطراب النظم",
    "ذبحة صدرية",
    "احتشاء عضلة القلب",
    "أمراض صمامات القلب",
    "مرض الشرايين المحيطية",
    # الجهاز التنفسي
    "الربو",
    "مرض الانسداد المزمن",
    "التهاب الشعب الهوائية",
    "الالتهاب الرئوي",
    "الانسداد الرئوي",
    "السل",
    "توقف التنفس أثناء النوم",
    # الجهاز الهضمي
    "ارتجاع المريء",
    "قرحة المعدة",
    "التهاب المعدة",
    "التهاب الكبد",
    "تليف الكبد",
    "التهاب البنكرياس",
    "مرض الأمعاء الالتهابي",
    "حصوات المرارة",
    # الأعصاب
    "الصرع",
    "الشقيقة (الصداع النصفي)",
    "مرض باركنسون",
    "ألزهايمر",
    "التصلب المتعدد",
    "اعتلال الأعصاب المحيطية",
    "السكتة الدماغية",
    # النفسية
    "الاكتئاب",
    "اضطراب القلق",
    "الاضطراب ثنائي القطب",
    "الفصام",
    "الوسواس القهري",
    "الأرق",
    # الغدد الصماء
    "قصور الغدة الدرقية",
    "فرط الغدة الدرقية",
    "متلازمة كوشينغ",
    "أديسون",
    # العضلات والعظام
    "الفصال العظمي",
    "التهاب المفاصل الروماتويدي",
    "هشاشة العظام",
    "آلام الظهر",
    "النقرس",
    # الكلى
    "المرض الكلوي المزمن",
    "حصوات الكلى",
    "التهاب المسالك البولية",
    # الدم
    "فقر الدم",
    "فقر الدم المنجلي",
    "الثالاسيميا",
    "اللوكيميا",
    "الليمفوما",
    # الأورام
    "سرطان الثدي",
    "سرطان الرئة",
    "سرطان القولون والمستقيم",
    "سرطان الكبد",
    "سرطان البروستاتا",
    # المناعة الذاتية
    "الذئبة الحمراء",
    "التهاب المفاصل الروماتويدي",
    "تصلب الجلد",
    "الصدفية",
    # الحساسية
    "حساسية الأدوية",
    "حضائيات الطعام",
    "حساسية اللاتكس",
    "حساسية البنسلين",
    "حساسية السلفا",
    # أخرى
    "قصور الغدة الدرقية",
    "ارتفاع lipids الدم",
    "تضخم البروستاتا الحميد",
    "المياه الزرقاء",
    "إعتام عدسة العين",
    "الألم المزمن",
    "اضطراب النوم",
]


def get_medications(language="en"):
    """Get medication list based on language"""
    if language == "ar":
        return MEDICATIONS_AR
    return MEDICATIONS_EN


def get_diagnoses(language="en"):
    """Get diagnosis list based on language"""
    if language == "ar":
        return DIAGNOSES_AR
    return DIAGNOSES_EN


def search_medications(query, language="en"):
    """Search medications by partial match"""
    medications = get_medications(language)
    query = query.lower()
    return [m for m in medications if query in m.lower()][:10]


def search_diagnoses(query, language="en"):
    """Search diagnoses by partial match"""
    diagnoses = get_diagnoses(language)
    query = query.lower()
    return [d for d in diagnoses if query in d.lower()][:10]
