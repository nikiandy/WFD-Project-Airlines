from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .models import User, UserProfile
from bookings.models import Booking
import uuid

def index(
    context = {
        'title': 'Account Management'
    }

    if request.user.is_authenticated:
        context['user'] = request.user

        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:

            profile = UserProfile.objects.create(user=request.user)

        context['profile'] = profile
        context['last_login'] = request.user.last_login
        context['date_joined'] = request.user.date_joined

        try:
            context['recent_bookings'] = Booking.objects.filter(user=request.user).order_by('-created_at')[:3]
        except Exception:
            context['recent_bookings'] = []

    return render(request, 'accounts/index.html', context)

def login_view(
    if request.user.is_authenticated:
        return redirect('accounts:index')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            if not remember:
                request.session.set_expiry(0)

            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('accounts:index')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'accounts/login.html', {
        'title': 'Login'
    })

def signup_view(
    if request.user.is_authenticated:
        return redirect('accounts:index')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return render(request, 'accounts/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken.')
            return render(request, 'accounts/signup.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/signup.html')

        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'accounts/signup.html')

        try:
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=make_password(password1),
                role='customer'
            )

            UserProfile.objects.create(user=user)

            login(request, user)
            messages.success(request, f'Welcome to Sky Airlines, {first_name}! Your account has been created successfully.')
            return redirect('accounts:index')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'accounts/signup.html', {
        'title': 'Sign Up'
    })

def logout_view(
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

def password_reset(
    if request.method == 'POST':
        email = request.POST.get('email')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            token = str(uuid.uuid4())
            user.profile.password_reset_token = token
            user.profile.save()

            reset_link = f"{request.scheme}://{request.get_host()}/accounts/reset-password/{token}/"

            try:
                send_mail(
                    'Reset Your Sky Airlines Password',
                    f'Hello {user.first_name},\n\nYou requested a password reset. Please click the link below to reset your password:\n\n{reset_link}\n\nIf you did not request this, please ignore this email.\n\nSky Airlines Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Password reset link has been sent to your email address.')
            except Exception as e:
                messages.error(request, f'Failed to send email: {str(e)}')
        else:
            messages.success(request, 'If your email is registered, you will receive a password reset link shortly.')

        return redirect('accounts:login')

    return render(request, 'accounts/password_reset.html', {
        'title': 'Reset Password'
    })

@login_required

def profile(
    user = request.user
    profile = user.profile

    recent_bookings = Booking.objects.filter(user=user).order_by('-created_at')[:5]

    if request.method == 'POST':
        try:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.save()

            profile.phone_number = request.POST.get('phone_number')
            profile.address = request.POST.get('address')

            dob = request.POST.get('date_of_birth')
            if dob:
                profile.date_of_birth = dob

            profile.passport_number = request.POST.get('passport_number')
            profile.nationality = request.POST.get('nationality')
            profile.save()

            messages.success(request, 'Profile updated successfully')

        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')

    context = {
        'title': 'My Profile',
        'user': user,
        'profile': profile,
        'recent_bookings': recent_bookings
    }

    return render(request, 'accounts/profile.html', context)

@login_required

def edit_profile(
    user = request.user
    profile = user.profile

    context = {
        'title': 'Edit Profile',
        'user': user,
        'profile': profile
    }

    return render(request, 'accounts/edit_profile.html', context)

@login_required

    if not request.user.is_staff and request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('accounts:index')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not role in ['admin', 'planning_manager', 'staff']:
            messages.error(request, 'Invalid role selected.')
            return render(request, 'accounts/create_staff.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return render(request, 'accounts/create_staff.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken.')
            return render(request, 'accounts/create_staff.html')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'accounts/create_staff.html')

        try:
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=make_password(password),
                role=role,
                is_staff=True if role in ['admin', 'planning_manager'] else False
            )

            UserProfile.objects.create(user=user)

            messages.success(request, f'Account for {first_name} {last_name} with role {role} has been created successfully.')
            return redirect('accounts:index')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'accounts/create_staff.html', {
        'title': 'Create Staff Account'
    })
