from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.forms import UserRegisterForm


def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            # new_user.is_active = False  # Отключаем проверку активности
            new_user.is_active = True     # Аккаунт сразу активен
            new_user.save()

            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Account successfully created! Welcome, {username}!"
            )
            # send_confirmation_email(request, new_user)  # Отключаем отправку email
            return redirect("core:index")
    else:
        form = UserRegisterForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/sign-up.html", context)