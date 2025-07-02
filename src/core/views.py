from django.shortcuts import render


def index(request):
    return render(request, "index.html")


def pricing(request):
    return render(request, "core/pricing.html")
