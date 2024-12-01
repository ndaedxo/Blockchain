# DIDBlockchain\DIDBlockchain\urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls, get_docs_view
from .views import HomeView

from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('api/', include('apps.api.urls')),
    path('docs/', include_docs_urls(title='DID Blockchain API')),
    path('schema/', get_schema_view(title='DID Blockchain API Schema')),
    path('users/', include('apps.users.urls')),
    path('webapp/', include('apps.webapp.urls')),
]

