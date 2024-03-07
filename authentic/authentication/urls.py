from django.urls import path
from . import views

urlpatterns = [
    path("entrar/", views.AuthenticTokenObtainPairView.as_view()),
    path("verificar/", views.AuthenticTokenVerifyView.as_view()),
    path("renovar/", views.AuthenticTokenRefreshView.as_view()),
    path("sair/", views.LogoutView.as_view()),
]
