from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import FormView, DetailView
from django.urls import reverse_lazy
from .forms import LoginForm, RegisterForm, ProfileForm
from .models import User


def main_page(request):
    return render(request, 'home.html')


class LoginView(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)

        else:
            form.add_error(None, "Invalid username or password")
            return self.form_invalid(form)


class RegisterView(FormView):
    template_name = 'users/registration.html'
    form_class = RegisterForm
    success_url = 'home'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class ProfileView(DetailView):
    model = User
    form_class = ProfileForm
    template_name = 'users/profile.html'

    def get_object(self, queryset=None):
        return self.request.user


def logout_view(request):
    logout(request)
    return redirect("home")