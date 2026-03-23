"""Views for the Accounts app."""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
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
        identifier = request.POST.get("national_id")
        password = request.POST.get("password")

        # Try to find user by National ID or Phone Number
        try:
            user_obj = User.objects.get(national_id=identifier)
        except User.DoesNotExist:
            try:
                user_obj = User.objects.get(phone_number=identifier)
            except User.DoesNotExist:
                messages.error(request, "Invalid National ID/Phone Number or password.")
                return render(request, "accounts/login.html")

        user = authenticate(username=user_obj.username, password=password)

        if user is not None:
            login(request, user)

            # Check if user has a completed medical profile - redirect to profile edit if not
            from profiles.models import MedicalProfile

            try:
                profile = MedicalProfile.objects.get(user=user)
                # Check if profile has been completed (has meaningful data)
                # Profile is incomplete if blood_type is still "Unknown" and no date_of_birth
                profile_incomplete = (
                    profile.blood_type == "Unknown" and not profile.date_of_birth
                )
            except MedicalProfile.DoesNotExist:
                profile_incomplete = True

            if profile_incomplete:
                # First login - redirect to create/edit profile
                return redirect("profile-edit")

            next_url = request.GET.get("next", "dashboard")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid National ID/Phone Number or password.")

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
        license_image = request.FILES.get("license_image", None)

        # Validation
        errors = []

        # Check terms acceptance
        accept_terms = request.POST.get("accept_terms")
        if not accept_terms:
            errors.append(
                "You must accept the Privacy Policy and Terms of Use to create an account."
            )

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
                license_image=license_image if profile_role == "doctor" else None,
            )

            # Set is_approved_doctor to False for doctor accounts (requires admin approval)
            if profile_role == "doctor":
                user.is_approved_doctor = False
                user.save()

            # Set appropriate message based on role
            if profile_role == "doctor":
                messages.success(
                    request,
                    "Registration successful! Your doctor account is pending approval.",
                )
            else:
                messages.success(request, "Registration successful! Please login.")

            # Verification is disabled for now - can be enabled in future
            # from .verification import send_email_verification, send_phone_otp
            # if user.email:
            #     send_email_verification(user, request)
            # if user.phone_number:
            #     send_phone_otp(user)

            return redirect("login")

    return render(request, "accounts/register.html")


def logout_view(request):
    """Logout and redirect to login."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


# ==================== Verification Views ====================


def verify_email_view(request, token):
    """Verify user's email address using token."""
    from .models import SyraUser

    try:
        user = SyraUser.objects.get(email_verification_token=token)
        if not user.is_email_verified:
            user.is_email_verified = True
            user.email_verification_token = ""
            user.save()
            messages.success(request, "Your email has been verified successfully!")
        else:
            messages.info(request, "Your email is already verified.")
    except SyraUser.DoesNotExist:
        messages.error(request, "Invalid verification token.")

    return redirect("login")


def verify_phone_view(request):
    """Verify user's phone number using OTP."""
    from .models import SyraUser
    from .verification import verify_phone_otp

    if request.method == "POST":
        otp = request.POST.get("otp", "")
        user_id = request.POST.get("user_id", "")

        try:
            user = SyraUser.objects.get(id=user_id)
            if verify_phone_otp(user, otp):
                messages.success(request, "Your phone number has been verified!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid or expired OTP. Please try again.")
        except SyraUser.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, "accounts/verify_phone.html")


def resend_otp_view(request):
    """Resend OTP to user's phone number."""
    from .models import SyraUser
    from .verification import send_phone_otp

    if request.method == "POST":
        user_id = request.POST.get("user_id", "")

        try:
            user = SyraUser.objects.get(id=user_id)
            if send_phone_otp(user):
                messages.success(request, "OTP has been resent to your phone.")
            else:
                messages.error(
                    request, "Failed to send OTP. Please check your phone number."
                )
        except SyraUser.DoesNotExist:
            messages.error(request, "User not found.")

    return redirect("verify_phone")


# ==================== Admin Views ====================


@login_required
def admin_doctor_approvals_view(request):
    """
    Admin view to see pending doctor account approvals.
    Only accessible by admin users.
    """
    from .models import SyraUser

    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect("dashboard")

    # Get pending doctors
    pending_doctors = SyraUser.objects.filter(
        profile_role="doctor", is_approved_doctor=False
    ).order_by("-date_joined")

    # Get approved doctors
    approved_doctors = SyraUser.objects.filter(
        profile_role="doctor", is_approved_doctor=True
    ).order_by("-date_joined")

    context = {
        "pending_doctors": pending_doctors,
        "approved_doctors": approved_doctors,
    }
    return render(request, "accounts/admin_doctor_approvals.html", context)


@login_required
@require_http_methods(["POST"])
def approve_doctor_view(request):
    """
    Approve a doctor account.
    """
    from .models import SyraUser

    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect("dashboard")

    doctor_id = request.POST.get("doctor_id")

    try:
        doctor = SyraUser.objects.get(id=doctor_id, profile_role="doctor")
        doctor.is_approved_doctor = True
        doctor.save()
        messages.success(request, f"Doctor {doctor.username} has been approved!")
    except SyraUser.DoesNotExist:
        messages.error(request, "Doctor not found.")

    return redirect("admin-doctor-approvals")


@login_required
@require_http_methods(["POST"])
def reject_doctor_view(request):
    """
    Reject/delete a doctor account application.
    """
    from .models import SyraUser

    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect("dashboard")

    doctor_id = request.POST.get("doctor_id")

    try:
        doctor = SyraUser.objects.get(id=doctor_id, profile_role="doctor")
        username = doctor.username
        doctor.delete()
        messages.success(
            request, f"Doctor application for {username} has been rejected."
        )
    except SyraUser.DoesNotExist:
        messages.error(request, "Doctor not found.")

    return redirect("admin-doctor-approvals")


@login_required
def doctor_detail_view(request, doctor_id):
    """
    Admin view to see detailed information about a specific doctor.
    Only accessible by admin users.
    """
    from .models import SyraUser

    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect("dashboard")

    try:
        doctor = SyraUser.objects.get(id=doctor_id, profile_role="doctor")
    except SyraUser.DoesNotExist:
        messages.error(request, "Doctor not found.")
        return redirect("admin-doctor-approvals")

    context = {
        "doctor": doctor,
    }
    return render(request, "accounts/doctor_detail.html", context)


@login_required
@require_http_methods(["POST"])
def revoke_doctor_view(request):
    """
    Revoke a doctor's authority (set is_approved_doctor to False).
    """
    from .models import SyraUser

    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect("dashboard")

    doctor_id = request.POST.get("doctor_id")

    try:
        doctor = SyraUser.objects.get(id=doctor_id, profile_role="doctor")
        doctor.is_approved_doctor = False
        doctor.save()
        messages.success(
            request, f"Doctor authority for {doctor.username} has been revoked."
        )
    except SyraUser.DoesNotExist:
        messages.error(request, "Doctor not found.")

    return redirect("admin-doctor-approvals")


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
    """API endpoint for user login using National ID or Phone Number."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    identifier = serializer.validated_data["national_id"]
    password = serializer.validated_data["password"]

    # Try to find user by National ID or Phone Number
    try:
        user = User.objects.get(national_id=identifier)
    except User.DoesNotExist:
        try:
            user = User.objects.get(phone_number=identifier)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
            )

    user = authenticate(username=user.username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if user has a completed medical profile
    from profiles.models import MedicalProfile

    try:
        profile = MedicalProfile.objects.get(user=user)
        # Check if profile has been completed (has meaningful data)
        profile_incomplete = (
            profile.blood_type == "Unknown" and not profile.date_of_birth
        )
    except MedicalProfile.DoesNotExist:
        profile_incomplete = True

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "user": SyraUserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Login successful.",
            "profile_incomplete": profile_incomplete,
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
