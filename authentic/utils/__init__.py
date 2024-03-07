from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from uuid import UUID


def encode_uid(pk):
    if isinstance(pk, UUID):
        uid_bytes = force_bytes(UUID(str(pk)).bytes)
        return urlsafe_base64_encode(uid_bytes)
    else:
        return force_str(urlsafe_base64_encode(force_bytes(pk)))


def decode_uid(uid):
    uid_bytes = urlsafe_base64_decode(uid)
    try:
        uid_uuid = UUID(bytes=uid_bytes)
        return uid_uuid
    except ValueError:
        return force_str(uid_bytes)


def get_allowed_fields(cls, fields: list = []) -> tuple:
    hidden_fields = [] + fields
    reserved_fields = tuple(
        field.__str__().split(".")[-1]
        for field in cls._meta.fields
        if field.__str__().split(".")[-1]
        not in ["password", "is_superuser", "is_staff"] + hidden_fields
    )
    return reserved_fields


def get_user_email(user):
    email_field_name = get_email_field_name(user)
    return getattr(user, email_field_name, None)


def get_email_field_name(user):
    return user.get_email_field_name()
