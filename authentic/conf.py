from django.apps import apps
from django.conf import settings as django_settings
from django.test.signals import setting_changed
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

AUTHENTIC_SETTINGS_NAMESPACE = "AUTHENTIC"


auth_module, auth_model = django_settings.AUTH_USER_MODEL.split(".")

User = apps.get_model(auth_module, auth_model)


class ObjDict(dict):
    def __getattribute__(self, item):
        try:
            val = self[item]
            if isinstance(val, str):
                val = import_string(val)
            elif isinstance(val, (list, tuple)):
                val = [import_string(v) if isinstance(v, str) else v for v in val]
            self[item] = val
        except KeyError:
            val = super().__getattribute__(item)

        return val


default_settings = {
    "USER_MODEL": User,
    "USER_ID_FIELD": User._meta.pk.name,
    "LOGIN_FIELD": User.USERNAME_FIELD,
    "EMAIL_ACTIVATION": True,
    "EMAIL_ACTIVATION_URL": "/contas/ativacao/{uid}/{token}",
    "CHANGE_PASSWORD_URL": "/contas/recuperar/senha/trocar/{uid}/{token}",
    "USER_CREATE_PASSWORD_RETYPE": False,
    "CHANGE_PASSWORD_RETYPE": False,
    "SEND_ACTIVATION_EMAIL": False,
    "EMAIL_RECOVER_PASSWORD": True,
    "AUTH_COOKIE": "access",
    "AUTH_COOKIE_MAX_AGE": 30 * 24 * 60 * 60 * 60,
    "AUTH_COOKIE_SECURE": True,
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_PATH": "/",
    "AUTH_COOKIE_SAMESITE": "None",
    "USER_MODEL_FIELDS_HIDDEN": [],
    "PAGE_SIZE": 10,
    "EMAIL": ObjDict(
        {
            "activation": "authentic.utils.email.ActivationEmail",
            "recover_password": "authentic.utils.email.RecoverPasswordEmail",
        },
    ),
    "PAGINATION": ObjDict(
        {"limitoffset": "authentic.utils.pagination.AuthenticPagination"}
    ),
    "MESSAGES": ObjDict(
        {
            "errors": "authentic.errors.AuthenticMessages",
        },
    ),
    "SERIALIZERS": ObjDict(
        {
            "user": "authentic.serializers.UserSerializer",
            "user_create": "authentic.serializers.UserCreateSerializer",
            "user_create_retype": "authentic.serializers.UserCreatePasswordRetypeSerializer",
            "activation": "authentic.serializers.UidTokenActivationSerializer",
            "resend_activation": "authentic.serializers.ResendActivationEmailSerializer",
            "recover_password": "authentic.serializers.RecoverPasswordSerializer",
            "change_password": "authentic.serializers.ChangePasswordSerializer",
            "change_password_retype": "authentic.serializers.ChangePasswordRetypeSerializer",
        }
    ),
    "PERMISSIONS": ObjDict(
        {
            "user": [
                "authentic.permissions.CurrentUserOrAdmin",
            ],
            "create": ["rest_framework.permissions.AllowAny"],
            "activation": ["rest_framework.permissions.AllowAny"],
            "resend_activation": ["rest_framework.permissions.AllowAny"],
            "recover_password": ["rest_framework.permissions.AllowAny"],
            "change_password": ["rest_framework.permissions.AllowAny"],
        }
    ),
    "AUTHENTICATION": ObjDict(
        {
            "authentic": [
                "authentic.authentication.authenticator.AuthenticJWTAuthentication",
            ],
        },
    ),
    "ALLOWED_HTTP_METHODS": ObjDict(
        {
            "get": ["get"],
            "post": ["post"],
            "delete": ["delete"],
            "patch": ["patch"],
        }
    ),
}


class Settings:
    def __init__(self, default_settings, explicit_overriden_settings: dict = None):
        if explicit_overriden_settings is None:
            explicit_overriden_settings = {}

        overriden_settings = (
            getattr(django_settings, AUTHENTIC_SETTINGS_NAMESPACE, {})
            or explicit_overriden_settings
        )

        self._load_default_settings()
        self._override_settings(overriden_settings)

    def _load_default_settings(self):
        for setting_name, setting_value in default_settings.items():
            if setting_name.isupper():
                setattr(self, setting_name, setting_value)

    def _override_settings(self, overriden_settings: dict):
        for setting_name, setting_value in overriden_settings.items():
            value = setting_value
            if isinstance(setting_value, dict):
                value = getattr(self, setting_name, {})
                value.update(ObjDict(setting_value))
            setattr(self, setting_name, value)


class LazySettings(LazyObject):
    def _setup(self, explicit_overriden_settings=None):
        self._wrapped = Settings(default_settings, explicit_overriden_settings)


settings = LazySettings()


def reload_authentic_settings(*args, **kwargs):
    global settings
    setting, value = kwargs["setting"], kwargs["value"]
    if setting == AUTHENTIC_SETTINGS_NAMESPACE:
        settings._setup(explicit_overriden_settings=value)


setting_changed.connect(reload_authentic_settings)
