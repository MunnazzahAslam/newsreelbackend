from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password

import phonenumbers
from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import PhoneVerification
from utils.jwt_token import encode_token, decode_token, blacklist_token


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'avatar_thumbnail', 'rating', 'own_reviews', 'is_top_rated')
        read_only_fields = ('id', 'username', 'avatar_thumbnail', 'rating', 'own_reviews', 'is_top_rated')


class UserDetailSerializer(serializers.ModelSerializer):
    is_reviewed = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone_number', 'avatar', 'avatar_thumbnail', 'facebook', 'twitter',
                  'linkedin', 'bio', 'posts', 'reviews', 'own_reviews', 'comments', 'subscribers', 'rating', 'ethics',
                  'trust', 'accuracy', 'fairness', 'contribution', 'expertise', 'is_top_rated', 'is_reviewed',
                  'is_subscribed')
        read_only_fields = ('id', 'email', 'phone_number', 'avatar_thumbnail', 'posts', 'reviews', 'own_reviews',
                            'comments', 'subscribers', 'rating', 'ethics', 'trust', 'accuracy', 'fairness',
                            'contribution', 'expertise', 'is_top_rated')

    def get_is_reviewed(self, obj):
        author_id = self.context['request'].user.id
        return obj.review_set.filter(author_id=author_id).exists()

    def get_is_subscribed(self, obj):
        user_id = self.context['request'].user.id
        return obj.followers.filter(user_id=user_id).exists()

    def update(self, instance, validated_data):
        if 'avatar' in validated_data:
            instance.avatar_thumbnail = validated_data['avatar']

        return super().update(instance, validated_data)


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password', 'avatar')
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }

    def validate_phone_number(self, phone_number):
        phone_number_obj = phonenumbers.parse(phone_number, 'US')
        if not phonenumbers.is_valid_number_for_region(phone_number_obj, 'US'):
            raise ValidationError('Not USA phone number')

        return phone_number

    def validate_password(self, password):
        validate_password(password)
        return password

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            phone_number=validated_data['phone_number']
        )
        user.set_password(validated_data['password'])
        user.save()

        # Update user, so we can use user id for path
        user.avatar = validated_data['avatar']
        user.avatar_thumbnail = validated_data['avatar']
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    password = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs['phone_number']
        password = attrs['password']

        user = authenticate(phone_number=phone_number, password=password)

        if not user:
            msg = _('Unable to log in with provided credentials.')
            raise ValidationError(msg)

        attrs['user'] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, data):
        try:
            token = RefreshToken(data['refresh_token'])
        except TokenError:
            raise ValidationError({'refresh_token': 'Invalid token'})

        data['exp'] = token.payload['exp']
        return data

    def create(self, validated_data):
        request = self.context['request']
        # Blacklist Access Token
        token = str(request._auth)
        exp = request._auth['exp']
        blacklist_token(token, exp)

        # Blacklist Refresh Token
        blacklist_token(validated_data['refresh_token'], validated_data['exp'])
        return True


class PhoneVerificationConfirmSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, data):
        user = self.context['user']
        phone_verification_obj = PhoneVerification.objects.filter(user=user, code=data['code']).last()
        if not phone_verification_obj:
            raise ValidationError({'code': 'Invalid code'})

        time_diff = timezone.now() - phone_verification_obj.created_at
        minutes = time_diff.seconds / 60
        if minutes > settings.PHONE_VERIFICATION_CODE_LIFETIME:
            raise ValidationError({'code': _('Code is expired')})

        return data

    def create(self, validated_data):
        user = self.context['user']
        user.is_verified_phone_number = True
        user.save()
        PhoneVerification.objects.filter(user=user).delete()
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise ValidationError(_("Email doesn't exist."))

        return email

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        token = encode_token({'id': user.id})
        send_mail(
            'Reset password',
            f'{settings.FRONTEND_DOMAIN}/reset-password/{token}/confirm/',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return token


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        token = data['token']
        decoded_data = decode_token(token)
        if not decoded_data:
            raise ValidationError({'token': _('Invalid or expired token.')})

        password = data['password']
        validate_password(password)
        data['user_id'] = decoded_data['id']
        return data

    def create(self, validated_data):
        user = User.objects.get(id=validated_data['user_id'])
        user.set_password(validated_data['password'])
        user.save()
        return user
