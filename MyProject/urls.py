from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  # if you're using a simple template

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('app.urls')),
]
