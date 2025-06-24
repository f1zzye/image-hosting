from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

from accounts.forms import UserRegisterForm

from common.mixins import TitleMixin


User = get_user_model()


def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            # new_user.is_active = False  # Отключаем проверку активности
            new_user.is_active = True  # Аккаунт сразу активен
            new_user.save()

            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Account successfully created! Welcome, {username}!"
            )
            # send_confirmation_email(request, new_user)  # Отключаем отправку email
            return redirect("core:index")
    else:
        form = UserRegisterForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/sign-up.html", context)


def login_view(request):
    # if request.user.is_authenticated:
    #     messages.warning(request, f"You are already logged in.")
    #     return redirect("core:index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # user = User.objects.get(email=email)
            # if not user.is_active:
            #     messages.warning(
            #         request, "Please confirm your email to activate your account."
            #     )
            #     return render(request, "userauths/sign-in.html")

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}")
                return redirect("core:index")
            else:
                messages.error(request, "The password is incorrect. Please try again.")
        except User.DoesNotExist:
            messages.warning(request, f"User with email {email} does not exist.")

    return render(request, "accounts/sign-in.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You are logged out.")
    return redirect("core:index")
