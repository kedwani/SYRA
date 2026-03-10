from django.urls import path
from Accounts.template_views import login_view, logout_view, register_view
from Profiles.template_views import (
    add_contact_view,
    add_history_view,
    add_medication_view,
    dashboard_view,
    delete_contact_view,
    delete_history_view,
    delete_medication_view,
    emergency_view,
    insurance_view,
    search_view,
    update_general_view,
    update_medical_view,
    edit_profile_view,
)

urlpatterns = [
    path("", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("profile/<str:username>/", dashboard_view, name="dashboard"),
    path("profile/<str:username>/edit/", edit_profile_view, name="edit_profile"),
    path(
        "profile/<str:username>/update/general/",
        update_general_view,
        name="update_general",
    ),
    path(
        "profile/<str:username>/update/medical/",
        update_medical_view,
        name="update_medical",
    ),
    path("profile/<str:username>/insurance/", insurance_view, name="insurance"),
    path("profile/<str:username>/contacts/add/", add_contact_view, name="add_contact"),
    path(
        "profile/<str:username>/contacts/<int:pk>/delete/",
        delete_contact_view,
        name="delete_contact",
    ),
    path(
        "profile/<str:username>/medications/add/",
        add_medication_view,
        name="add_medication",
    ),
    path(
        "profile/<str:username>/medications/<int:pk>/delete/",
        delete_medication_view,
        name="delete_medication",
    ),
    path("profile/<str:username>/history/add/", add_history_view, name="add_history"),
    path(
        "profile/<str:username>/history/<int:pk>/delete/",
        delete_history_view,
        name="delete_history",
    ),
    path("search/", search_view, name="search"),
    path("emergency/<uuid:public_id>/", emergency_view, name="emergency"),
]
