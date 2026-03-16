"""Views for the Accounts app."""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample

from .serializers import SyraUserSerializer, RegisterSerializer, LoginSerializer

User = get_user_model()


# ==================== Template Views ====================


@csrf_protect
@ratelimit(key="ip", rate="10/m", method="POST")
def login_template_view(request):
    """HTML login page."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        national_id = request.POST.get("national_id")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(national_id=national_id)
            user = authenticate(username=user_obj.username, password=password)

            if user is not None:
                login(request, user)
                next_url = request.GET.get("next", "dashboard")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid National ID or password.")
        except User.DoesNotExist:
            messages.error(request, "Invalid National ID or password.")

    return render(request, "accounts/login.html")


@csrf_protect
@ratelimit(key="ip", rate="3/h", method="POST")
def register_template_view(request):
    """HTML registration page."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        national_id = request.POST.get("national_id")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        phone_number = request.POST.get("phone_number", "")
        date_of_birth = request.POST.get("date_of_birth", None)
        gender = request.POST.get("gender", "")
        nationality = request.POST.get("nationality", "")
        profile_role = request.POST.get("profile_role", "user")
        license_number = request.POST.get("license_number", "")
        specialty = request.POST.get("specialty", "")

        # Validation
        errors = []

        if password != password_confirm:
            errors.append("Passwords do not match.")

        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")

        if not national_id or len(national_id) != 14 or not national_id.isdigit():
            errors.append("National ID must be exactly 14 digits.")

        if User.objects.filter(national_id=national_id).exists():
            errors.append("This National ID is already registered.")

        if User.objects.filter(username=username).exists():
            errors.append("Username already exists.")

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Parse date of birth if provided
            from datetime import date

            dob = None
            if date_of_birth:
                try:
                    dob = date.fromisoformat(date_of_birth)
                except ValueError:
                    dob = None

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                national_id=national_id,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                date_of_birth=dob,
                gender=gender,
                nationality=nationality,
                profile_role=profile_role,
                license_number=license_number if profile_role == "doctor" else "",
                specialty=specialty if profile_role == "doctor" else "",
            )

            # Set appropriate message based on role
            if profile_role == "doctor":
                messages.success(
                    request,
                    "Registration successful! Your doctor account is pending approval.",
                )
            else:
                messages.success(request, "Registration successful! Please login.")
            return redirect("login")

    return render(request, "accounts/register.html")


def logout_view(request):
    """Logout and redirect to login."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


# ==================== API Views ====================


class RegisterView(generics.CreateAPIView):
    """API endpoint for user registration."""

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @method_decorator(ratelimit(key="ip", rate="3/h", method="POST"))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": SyraUserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "User registered successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    methods=["POST"],
    request=LoginSerializer,
    responses=SyraUserSerializer,
    examples=[
        OpenApiExample(
            "Login Example",
            value={"national_id": "12345678901234", "password": "password123"},
            request_only=True,
        ),
    ],
)
@api_view(["POST"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="10/m", method="POST")
def login_view(request):
    """API endpoint for user login using National ID."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    national_id = serializer.validated_data["national_id"]
    password = serializer.validated_data["password"]

    try:
        user = User.objects.get(national_id=national_id)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
        )

    user = authenticate(username=user.username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "user": SyraUserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Login successful.",
        }
    )


@extend_schema(
    methods=["GET"],
    responses=SyraUserSerializer,
)
@extend_schema(
    methods=["PUT"],
    request=SyraUserSerializer,
    responses=SyraUserSerializer,
)
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """API endpoint to get or update current user profile."""
    if request.method == "GET":
        serializer = SyraUserSerializer(request.user)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = SyraUserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
