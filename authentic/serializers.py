from django.forms import ValidationError
from rest_framework import serializers
from rest_framework.settings import api_settings
from django.core import exceptions as django_exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from authentic.conf import settings
from django.db import IntegrityError, transaction
from authentic.utils import get_allowed_fields
from authentic.utils import decode_uid
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = get_allowed_fields(User, settings.USER_MODEL_FIELDS_HIDDEN)
        read_only_fields = get_allowed_fields(User, settings.USER_MODEL_FIELDS_HIDDEN)


class UserCreateMixin:
    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")
        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            # For custom accounts with  FK,ManyToMany and other relations
            # models, remember to set they null=True
            # the atomic create will not return a especific error
            user = User.objects.create_user(**validated_data)
            if settings.SEND_ACTIVATION_EMAIL:
                user.is_active = False
                user.save(update_fields=["is_active"])
        return user


class UserCreateSerializer(UserCreateMixin, serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    default_error_messages = {
        "cannot_create_user": settings.MESSAGES.errors.CANNOT_CREATE_USER_ERROR
    }

    class Meta:
        model = User
        fields = [User.USERNAME_FIELD] + User.REQUIRED_FIELDS + ["password"]

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )
        return attrs


class UserCreatePasswordRetypeSerializer(UserCreateSerializer):
    default_error_messages = {
        "password_mismatch": settings.MESSAGES.errors.PASSWORD_MISMATCH_ERROR
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["re_password"] = serializers.CharField(
            style={"input_type": "password"}
        )

    def validate(self, attrs):
        self.fields.pop("re_password", None)
        re_password = attrs.pop("re_password")
        attrs = super().validate(attrs)
        if attrs["password"] == re_password:
            return attrs
        else:
            key_error = "password_mismatch"
            raise ValidationError(
                {"password": [self.error_messages[key_error]]},
                code=key_error,
            )


class UidTokenActivationSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    default_error_messages = {
        "uid_error": settings.MESSAGES.errors.INVALID_UID_ERROR,
        "token_error": settings.MESSAGES.errors.INVALID_TOKEN_ERROR,
    }

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        try:
            uid = decode_uid(self.initial_data.get("uid", ""))
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            key_error = "uid_error"
            raise ValidationError(
                {"uid": [self.error_messages[key_error]]}, code=key_error
            )
        is_token_valid = default_token_generator.check_token(
            self.user, self.initial_data.get("token", "")
        )
        if is_token_valid:
            return validated_data
        else:
            key_error = "token_error"
            raise ValidationError(
                {"token": [self.error_messages[key_error]]}, code=key_error
            )


class ResendActivationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    default_error_messages = {
        "is_validated": settings.MESSAGES.errors.ALREADY_ACTIVATED,
        "wrong_email": settings.MESSAGES.errors.USER_NOT_EXISTS,
    }

    def validate(self, attrs):
        valited_data = super().validate(attrs)

        user = User.objects.filter(email=valited_data.get("email"))

        if not user.exists():
            raise serializers.ValidationError(
                {"email": [self.error_messages["wrong_email"]]}
            )

        if user.first().is_active:
            raise ValidationError({"email": [self.error_messages["is_validated"]]})

        return valited_data


class RecoverPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    default_error_messages = {"wrong_email": settings.MESSAGES.errors.USER_NOT_EXISTS}

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        user = User.objects.filter(email=validated_data.get("email"))

        if not user.exists():
            raise serializers.ValidationError(
                {"email": [self.error_messages["wrong_email"]]}
            )

        return validated_data


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        user = getattr(self, "user", None) or self.context["request"].user

        assert user is not None

        try:
            validate_password(attrs["new_password"], user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return super().validate(attrs)


class PasswordRetypeSerializer(PasswordSerializer):
    default_error_messages = {"password_mismatch": "ERROR"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["re_new_password"] = serializers.CharField(
            style={"input_type": "password"}
        )

    def validate(self, attrs):
        self.fields.pop("re_new_password", None)
        re_new_password = attrs.pop("re_new_password")
        attrs = super().validate(attrs)
        if attrs["new_password"] == re_new_password:
            return attrs
        else:
            self.fail("password_mismatch")


class ChangePasswordSerializer(UidTokenActivationSerializer, PasswordSerializer):
    pass


class ChangePasswordRetypeSerializer(
    UidTokenActivationSerializer, PasswordRetypeSerializer
):
    pass
