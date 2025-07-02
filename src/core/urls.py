from django.urls import include, path
from core.views import index, pricing


app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path("pricing/", pricing, name="pricing"),
]
