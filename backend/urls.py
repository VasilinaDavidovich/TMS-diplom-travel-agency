from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from typing import List

urlpatterns: List[path] = [
    path('admin/', admin.site.urls),

    # Frontend аутентификация
    path('api/auth/', include('accounts.urls')),

    # API аутентификация
    path('api/auth/api/', include('accounts.api.urls')),

    # API отелей
    path('api/', include('hotels.api.urls')),

    # Frontend страницы
    path('', include('hotels.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )