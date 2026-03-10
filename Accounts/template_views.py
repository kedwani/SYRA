"""
Accounts/template_views.py
"""

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import redirect, render

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect("web:dashboard", username=request.user.username)

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next")
            return redirect(next_url or "web:dashboard", username=user.username)
        else:
            return render(
                request,
                "accounts/login.html",
                {"form": {"errors": True}, "next": request.POST.get("next", "")},
            )

    return render(request, "accounts/login.html", {"next": request.GET.get("next", "")})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("web:dashboard", username=request.user.username)

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        national_id = request.POST.get("national_id", "").strip() or None
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        errors = {}

        if not username:
            errors["username"] = ["Username is required."]
        elif User.objects.filter(username=username).exists():
            errors["username"] = ["This username is already taken."]

        if not email:
            errors["email"] = ["Email is required."]
        elif User.objects.filter(email=email).exists():
            errors["email"] = ["An account with this email already exists."]

        if len(password) < 8:
            errors["password"] = ["Password must be at least 8 characters."]
        elif password != password_confirm:
            errors["password"] = ["Passwords do not match."]

        if national_id and len(national_id) != 14:
            errors["national_id"] = ["National ID must be exactly 14 digits."]

        if errors:
            form_data = {
                "errors": errors,
                "username": {"value": username},
                "email": {"value": email},
                "national_id": {"value": national_id or ""},
            }
            return render(request, "accounts/register.html", {"form": form_data})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            national_id=national_id,
        )
        login(request, user)
        messages.success(
            request,
            f"Welcome to SYRA, {username}! Your medical profile has been created.",
        )
        return redirect("web:dashboard", username=user.username)

    return render(request, "accounts/register.html", {"form": {}})


def logout_view(request):
    logout(request)
    return redirect("web:login")
