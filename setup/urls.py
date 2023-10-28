from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("authentication.urls")),
    path("main/", include("main.urls")),
    path("staff/", include("staff.urls")),
]
