from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages


User = get_user_model()


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Password do not match")
            return render(request, self.template_name)

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, self.template_name)

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, self.template_name)

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully. You can log in now.")
        return redirect("login")
