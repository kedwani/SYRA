# SYRA - Smart Medical ID System 🏥🇪🇬

**SYRA** is a specialized medical backend platform designed for the Egyptian market. It powers smart medical wristbands and cards equipped with QR codes and NFC technology, allowing first responders and doctors to access life-saving patient information in seconds.

## 🚀 The Problem

In emergency situations, every second counts. Many patients in Egypt carry critical medical data in paper form, which can be lost or inaccessible. **SYRA** digitizes this data securely.

## ✨ Key Features

* **Automated Medical Profiles:** Uses **Django Signals** to create a medical profile instantly upon user registration.
* **Privacy-First API:** Sensitive data like **Insurance Card Photos** are separated into specific endpoints.
* **Emergency Data Tracking:** Stores blood types, chronic diseases, medical history, and emergency contacts.

## 🛠️ Tech Stack

* **Framework:** Django 5.x / Django REST Framework (DRF)
* **Database:** SQLite
* **Language:** Python 3.13+

## 🔗 API Endpoints

| Feature | Endpoint | Method |
| --- | --- | --- |
| **User Profile** | `/api/profile/<username>/` | GET / PUT |
| **Insurance Data** | `/api/profile/<username>/insurance/` | GET |

---

## ⚙️ How to Run Locally

1. **Clone & Install:**
```bash
git clone https://github.com/kedwani/SYRA.git
cd SYRA
pip install django djangorestframework Pillow

```


2. **Migrate & Run:**
```bash
python manage.py migrate
python manage.py runserver

```



---

## 👨‍💻 Author

**Mahmoud Nasser (Kedwani)** - Backend Developer

