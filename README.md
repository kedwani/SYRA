SYRA Medical ID PlatformA hybrid medical identification platform designed for the Egyptian market, utilizing NFC and QR-enabled physical devices. SYRA empowers patients to store critical medical data securely and provides first responders with instant, life-saving access via a simple scan.🌟 Features👤 User Authentication & IdentityNational ID Integration: Registration requires a valid 14-digit Egyptian National ID.Smart Validation: Automatic extraction and validation of birth date and century from the National ID.Secure Access: JWT-based authentication for all private API interactions.🏥 Medical Profile ManagementComprehensive Data: Storage for blood type, allergies, chronic conditions, and immune diseases.Biometric Tracking: Height and weight tracking for accurate emergency dosing.💊 Medication & History TrackingMedication Logs: Track dosage, frequency, and duration (start/end dates).Surgical History: Logging of previous accidents, fractures, or major medical events with date tracking.👨‍👩‍👧‍👦 Emergency ContactsDual Contact Support: Quick access to up to two emergency contacts per profile.Instant Dialing: Optimized for mobile browser "click-to-call" functionality.🔒 Privacy & SecurityAt-Rest Encryption: Insurance card images are encrypted using Fernet symmetric encryption.Data Segregation: Sensitive insurance data is never included in the initial emergency scan; it is only accessible via an authenticated or specific secondary request.UUID Masking: Public emergency profiles use non-sequential UUIDs to prevent ID enumeration (Insecure Direct Object Reference protection).🛠 Tech StackTechnologyPurposePython 3.10+Backend languageDjango 5.xWeb frameworkDjango REST FrameworkAPI development & SerializationSimpleJWTStateless authenticationCryptography (Fernet)Secure data encryptionSQLite / PostgreSQLDatabase (Development / Production)Python-DecoupleEnvironment variable management📂 Project StructurePlaintextsyra/                    # Project Configuration
├── settings.py          # Custom User Model & JWT Config
├── urls.py              # Root Routing
accounts/                # User & Identity App
├── models.py            # SyraUser (National ID as Username)
├── validators.py        # 14-digit Egyptian ID logic
├── serializers.py       # Auth serialization
profiles/                # Medical Data App
├── models.py            # MedicalProfile, Medication, Contact, Event
├── encryption.py        # Fernet logic for insurance images
├── signals.py           # Auto-profile creation on user signup
templates/               # Mobile-First HTML Views
└── profiles/emergency.html  # The QR/NFC Landing Page
🚀 Installation1. PrerequisitesPython 3.10 or higher.Virtualenv package installed (pip install venv).2. Setup EnvironmentBash# Clone and enter project
git clone <repository-url>
cd syra-medical-id

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
3. Environment VariablesCreate a .env file in the root directory:Code snippetSECRET_KEY=your-django-secret-key
ENCRYPTION_KEY=your-fernet-key-generated-via-cryptography
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost
4. Initialize DatabaseBashpython manage.py migrate
python manage.py collectstatic
python manage.py runserver
📋 API ReferenceEmergency Access (Public)MethodEndpointDescriptionGET/emergency/<uuid>/HTML View: Optimized for QR/NFC scanningGET/api/profiles/scan/<uuid>/JSON View: Core medical data for appsMedical Management (Private - JWT Required)MethodEndpointDescriptionGET/PUT/api/profiles/my-profile/Manage personal medical dataGET/POST/api/profiles/medications/CRUD for current medicationsGET/POST/api/profiles/contacts/Manage emergency contacts (Max 2)🛡 Security HighlightsNational ID: Validated against the Egyptian Civil Status Organization format (Century-YYMMDD-SS-KKK-C).Image Security: Insurance photos are stored as encrypted blobs. The decryption key is managed through environment variables, ensuring data remains secure even if the database is compromised.Privacy: The emergency scan page excludes the National ID and Insurance Photo by default to prevent unauthorized data harvesting.👨‍💻 AuthorMahmoud – Backend Developer