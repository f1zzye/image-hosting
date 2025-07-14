import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View, ListView
from django.http import JsonResponse, Http404, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Image, TemporaryLink


class DeleteImageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        image_id = request.POST.get("image_id")
        if not image_id:
            return JsonResponse({"error": "Image ID is required"}, status=400)

        image = get_object_or_404(Image, id=image_id, user=request.user)
        image.delete()
        return JsonResponse({"success": True})


class CreateTemporaryLinkView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            image_id = data.get("image_id")

            if not image_id:
                return JsonResponse({"error": "Image ID is required"}, status=400)

            image = get_object_or_404(Image, id=image_id, user=request.user)

            temp_link = TemporaryLink.objects.create(
                image=image,
                user=request.user,
                expires_in_seconds=3600,
            )

            link_url = request.build_absolute_uri(
                reverse('images:temporary_link_view', kwargs={'link_id': temp_link.id})
            )

            return JsonResponse({
                'success': True,
                'link_url': link_url,
                'expires_at': temp_link.expires_at.isoformat(),
                'expires_in_seconds': temp_link.expires_in_seconds,
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class TemporaryLinkView(View):
    def get(self, request, link_id):
        temp_link = get_object_or_404(TemporaryLink, id=link_id)
        if not temp_link.is_valid():
            raise Http404("Temporary link is expired or already used")
        image_file = temp_link.image.original_image
        return HttpResponse(image_file, content_type='image/jpeg')