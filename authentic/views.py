from authentic.conf import settings
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.utils.timezone import now
from rest_framework.decorators import action
from authentic import utils
from typing import Any


User = settings.USER_MODEL


class UserViewSet(viewsets.ModelViewSet):
    pagination_class = settings.PAGINATION.limitoffset
    serializer_class = settings.SERIALIZERS.user
    permission_classes = settings.PERMISSIONS.user
    authentication_classes = settings.AUTHENTICATION.authentic
    queryset = User.objects.all()

    def get_queryset(self) -> Any:
        queryset = super().get_queryset()
        if self.action == "list":
            return self.paginate_queryset(self.queryset)
        return queryset

    def get_permissions(self):
        if self.action == "new_account":
            self.permission_classes = settings.PERMISSIONS.create
        if self.action == "activation":
            self.permission_classes = settings.PERMISSIONS.activation
        if self.action == "resend_activation":
            self.permission_classes = settings.PERMISSIONS.resend_activation
        if self.action == "recover_password":
            self.permission_classes = settings.PERMISSIONS.recover_password
        if self.action == "change_password":
            self.permission_classes = settings.PERMISSIONS.change_password
        return super().get_permissions()

    def get_http_methods_name(self):
        if self.action == "list":
            self.http_method_names = ["GET"]

    def get_serializer_class(self):
        self.get_http_methods_name()
        if self.action == "list":
            return settings.SERIALIZERS.user
        if self.action == "new_account":
            if settings.USER_CREATE_PASSWORD_RETYPE:
                return settings.SERIALIZERS.user_create_retype
            return settings.SERIALIZERS.user_create
        if self.action == "activation":
            return settings.SERIALIZERS.activation
        if self.action == "resend_activation":
            return settings.SERIALIZERS.resend_activation
        if self.action == "recover_password":
            return settings.SERIALIZERS.recover_password
        if self.action == "change_password":
            if settings.CHANGE_PASSWORD_RETYPE:
                return settings.SERIALIZERS.change_password_retype
            return settings.SERIALIZERS.change_password
        return self.serializer_class

    @action(["post"], detail=False, url_path="criar")
    def new_account(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(*args, **kwargs)
        user.is_active = False
        user.save()

        context = {
            "user": user,
        }
        to = [utils.get_user_email(user)]
        if settings.EMAIL_ACTIVATION:
            settings.EMAIL.activation(self.request, context).send(to)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(["post"], detail=False, url_path="ativacao")
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path="ativacao/reenviar")
    def resend_activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.data["email"])
        context = {"user": user}
        to = [utils.get_user_email(user)]
        if settings.EMAIL_ACTIVATION:
            settings.EMAIL.activation(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path="recuperar/senha")
    def recover_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.data["email"])
        context = {"user": user}
        to = [utils.get_user_email(user)]
        if settings.EMAIL_RECOVER_PASSWORD:
            settings.EMAIL.recover_password(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False, url_path="recuperar/senha/trocar")
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
