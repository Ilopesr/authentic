from django.utils.translation import gettext_lazy as _


class AuthenticMessages:
    INVALID_PASSWORD_ERROR = _("Invalid password.")
    PASSWORD_MISMATCH_ERROR = _("Mismatch password.")
    CANNOT_CREATE_USER_ERROR = _("Unable to create account.")
    INVALID_UID_ERROR = _("Invalid uid.")
    INVALID_TOKEN_ERROR = _("Invalid TOKEN.")
    ALREADY_ACTIVATED = _("User is already validated.")
    USER_NOT_EXISTS = _("Email is not exists.")
