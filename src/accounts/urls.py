from django.contrib.auth import views as auth_views
from django.urls import path

from src.accounts.views import register_view, login_view

app_name = "accounts"

urlpatterns = [
    path("sign-up/", register_view, name="sign-up"),
    path("sign-in/", login_view, name="sign-in"),
]
