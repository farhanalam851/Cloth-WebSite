from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from .forms import ProfileForm, RegisterForm, StyledAuthenticationForm
from .models import Profile


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = StyledAuthenticationForm


class CustomLogoutView(LogoutView):
    next_page = 'products:home'


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your business account has been created.')
            return redirect('products:home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    # get_or_create handles users that exist without a Profile row (e.g. a
    # superuser created via `createsuperuser`, which bypasses RegisterForm).
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile_obj)
    return render(request, 'accounts/profile.html', {'form': form})
