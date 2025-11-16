from django.shortcuts import render


def profile_page(request):
    """Frontend страница личного кабинета"""
    return render(request, 'profile.html')