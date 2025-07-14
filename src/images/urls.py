from django.urls import path

from .views import DeleteImageView

app_name = "images"

urlpatterns = [
    path("delete-image/", DeleteImageView.as_view(), name="delete-image"),
]
