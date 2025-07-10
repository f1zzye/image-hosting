from django import forms
from .models import Image


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ["original_image"]
        widgets = {
            "original_image": forms.FileInput(
                attrs={
                    "accept": "image/jpeg,image/jpg,image/png",
                    "multiple": False,
                    "style": "display: none;",
                    "id": "fileInput",
                }
            )
        }
