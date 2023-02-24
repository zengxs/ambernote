"""ambernote URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from .views import schema_view, spa_files_view

urlpatterns = []

if 'debug_toolbar' in settings.INSTALLED_APPS:
    # django-debug-toolbar
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    # django-admin
    urlpatterns += [path('dj-admin/', admin.site.urls)]

urlpatterns += [
    # Auth API
    path('api/auth/', include('ambernote.authx.urls')),
    # Core API
    path('api/', include('ambernote.amber.urls')),
    # API documentation
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # All other paths should be handled by the SPA
    # Exclude API, django-admin, and debug-toolbar paths
    re_path(r'^(?!api/|dj-admin/|__debug__/)(?P<path>.*)$', spa_files_view, name='spa-files-view'),
]
