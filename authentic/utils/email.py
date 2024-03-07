from templated_mail.mail import BaseEmailMessage
from django.contrib.auth.tokens import default_token_generator
from authentic import utils
from authentic.conf import settings


class ActivationEmail(BaseEmailMessage):
    template_name = "email/activation.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.EMAIL_ACTIVATION_URL.format(**context)
        return context


class RecoverPasswordEmail(BaseEmailMessage):
    template_name = "email/recover_password.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.CHANGE_PASSWORD_URL.format(**context)
        return context
