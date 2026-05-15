from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages

@login_required
@user_passes_test(lambda u: u.is_staff)
def user_list(request):
    users = User.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_staff)
def user_add(request):
    if request.method == 'POST':
        username   = request.POST.get('username')
        password   = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name  = request.POST.get('last_name')
        email      = request.POST.get('email')
        is_staff   = request.POST.get('is_staff') == 'on'

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('user_add')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        user.is_staff = is_staff
        user.save()
        messages.success(request, f'User "{username}" created successfully!')
        return redirect('user_list')

    return render(request, 'accounts/user_add.html')
from .models import ShopSettings

@login_required
@user_passes_test(lambda u: u.is_staff)
def shop_settings(request):
    settings = ShopSettings.objects.first()
    if not settings:
        settings = ShopSettings.objects.create()

    if request.method == 'POST':
        settings.shop_name   = request.POST.get('shop_name')
        settings.address     = request.POST.get('address')
        settings.phone       = request.POST.get('phone')
        settings.email       = request.POST.get('email')
        settings.gst_number  = request.POST.get('gst_number')

        if request.FILES.get('logo'):
            settings.logo = request.FILES['logo']

        settings.save()
        messages.success(request, 'Settings saved successfully!')
        return redirect('shop_settings')

    return render(request, 'accounts/settings.html', {'settings': settings})   