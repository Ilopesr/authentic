from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("contas", views.UserViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
