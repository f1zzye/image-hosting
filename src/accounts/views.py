from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from accounts.forms import UserRegisterForm
from common.mixins import TitleMixin

from accounts.services.emails import send_confirmation_email

User = get_user_model()


class UserRegisterView(TitleMixin, SuccessMessageMixin, CreateView):
    template_name = "accounts/sign-up.html"
    title = "Sign Up - PhotoHub"
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("core:index")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_active = False
        self.object.save()

        send_confirmation_email(self.request, self.object)

        username = form.cleaned_data.get("username")
        messages.success(self.request, f"Account created for {username}! Please check your email to activate your account.")

        return redirect(self.success_url)


def activate_account_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='accounts.auth_backend.EmailBackend')
        messages.success(request, "Your account has been successfully activated!")
        return redirect("core:index")
    else:
        messages.error(request, "Activation link is invalid!")
        return redirect("core:index")


class UserLoginView(TitleMixin, TemplateView):
    template_name = "accounts/sign-in.html"
    title = "Sign In - PhotoHub"

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_check = User.objects.get(email=email)
            if not user_check.is_active:
                messages.warning(
                    request,
                    "Please confirm your email to activate your account."
                )
                return self.render_to_response(self.get_context_data())

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}!")
                return redirect("core:index")
            else:
                messages.error(request, "The password is incorrect. Please try again.")

        except User.DoesNotExist:
            messages.warning(request, f"User with email {email} does not exist.")

        return self.render_to_response(self.get_context_data())


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("core:index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, "You are logged out.")
        return super().dispatch(request, *args, **kwargs)