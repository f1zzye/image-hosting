from django.urls import path

from .views import DeleteImageView, CreateTemporaryLinkView, TemporaryLinkView

app_name = "images"

urlpatterns = [
    path("delete-image/", DeleteImageView.as_view(), name="delete-image"),
    path('create-temporary-link/', CreateTemporaryLinkView.as_view(), name='create-temporary-link'),
    path('temporary-link/<uuid:link_id>/', TemporaryLinkView.as_view(), name='temporary_link_view'),
]
