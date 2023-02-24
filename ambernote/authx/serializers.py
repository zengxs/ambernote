from dj_rest_auth.registration.serializers import RegisterSerializer as BaseRegisterSerializer
from dj_rest_auth.serializers import LoginSerializer as BaseLoginSerializer, \
    UserDetailsSerializer as BaseUserDetailsSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

UserModel = get_user_model()


class RegisterSerializer(BaseRegisterSerializer):
    username = None  # type: ignore
    email = serializers.EmailField(required=True)
    fullname = serializers.CharField(required=True)
    password1 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def get_cleaned_data(self):
        """Override super method to add fullname field."""
        return {
            'email': self.validated_data.get('email', ''),
            'fullname': self.validated_data.get('fullname', ''),
            'password1': self.validated_data.get('password1', ''),
        }

    def custom_signup(self, request, user):
        """
        Perform custom signup logic after user is created.
        """
        with transaction.atomic():
            # Set fullname field
            user.fullname = self.validated_data.get('fullname', '')
            # If this is the first user, make it a superuser
            if UserModel.objects.count() == 1 and UserModel.objects.filter(uuid=user.uuid).exists():
                user.is_staff = True
                user.is_superuser = True
            user.save()


class LoginSerializer(BaseLoginSerializer):
    username = None  # type: ignore
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class UserDetailsSerializer(BaseUserDetailsSerializer):
    class Meta(BaseUserDetailsSerializer.Meta):
        model = UserModel
        fields = ('uuid', 'email', 'fullname')
        read_only_fields = ('uuid', 'email')
