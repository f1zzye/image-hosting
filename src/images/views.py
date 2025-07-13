from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View, ListView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Image


class DeleteImageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        image_id = request.POST.get("image_id")
        if not image_id:
            return JsonResponse({"error": "Image ID is required"}, status=400)

        image = get_object_or_404(Image, id=image_id, user=request.user)
        image.delete()
        return JsonResponse({"success": True})

