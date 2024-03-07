from django.urls import path, include

urlpatterns = [
    path("", include("authentic.urls")),
    path("", include("authentic.authentication.urls")),
]
