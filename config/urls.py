from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from rest_framework.permissions import AllowAny

from config import views

urlpatterns = [
    path("", views.index, name="index"),
    path("livez", views.livez, name="livez"),
    path("readyz", views.readyz, name="readyz"),
    path("admin/", admin.site.urls),
    # The schema is the one deliberately public API route.
    path("api/schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny]), name="schema"),
]

# Development serves static files through Django; Fly serves them from the image in production.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
