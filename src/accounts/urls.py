from django.urls import path

from accounts.views import UserRegisterView, UserLoginView, UserLogoutView

app_name = "accounts"

urlpatterns = [
    path("sign-up/", UserRegisterView.as_view(), name="sign-up"),
    path("sign-in/", UserLoginView.as_view(), name="sign-in"),
    path("sign-out/", UserLogoutView.as_view(), name="sign-out"),
]
