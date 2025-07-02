from django.urls import include, path

from core.views import IndexView, SubscriptionPlansView

app_name = "core"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("pricing/", SubscriptionPlansView.as_view(), name="pricing"),
]
