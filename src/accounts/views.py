from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

from accounts.forms import UserRegisterForm
from common.mixins import TitleMixin

User = get_user_model()


class UserRegisterView(TitleMixin, SuccessMessageMixin, CreateView):
    template_name = "accounts/sign-up.html"
    title = "Sign Up - PhotoHub"
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("core:index")
    success_message = "Account successfully created!"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_active = True
        self.object.save()

        username = form.cleaned_data.get("username")
        messages.success(self.request, f"Account successfully created for {username}!")

        return redirect(self.success_url)


class UserLoginView(TitleMixin, TemplateView):
    template_name = "accounts/sign-in.html"
    title = "Sign In - PhotoHub"

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
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