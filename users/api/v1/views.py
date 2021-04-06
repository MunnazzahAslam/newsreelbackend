from django.contrib.auth import get_user_model

from drf_yasg.utils import swagger_auto_schema

from rest_framework import status, generics
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.views import TokenRefreshView

from .schema import AuthSchema
from .serializers import (
    LoginSerializer,
    SignupSerializer,
    LogoutSerializer,
    UserDetailSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    PhoneVerificationConfirmSerializer,
)
from .permissions import IsOwnerUserProfile
from utils.utils import generate_and_send_phone_verification_number_code


User = get_user_model()


class SignupView(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(
        tags=['auth'], operation_description="Sign up", request_body=SignupSerializer(), responses={200: AuthSchema()}
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = {
            'id': user.id,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(
        tags=['auth'], operation_description="Login", request_body=LoginSerializer(), responses={200: AuthSchema()}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        data = {
            'id': user.id,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        return Response(data)


class LogoutApiView(APIView):

    @swagger_auto_schema(
        tags=['auth'], operation_description="Logout", request_body=LogoutSerializer(), responses={200: 'Success'}
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class PhoneVerificationView(APIView):

    @swagger_auto_schema(
        tags=['auth'], operation_description="Phone Verification", responses={200: 'Success', 500: 'Cannot send SMS'}
    )
    def post(self, request):
        is_sent = generate_and_send_phone_verification_number_code(request.user)
        if not is_sent:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)


class PhoneVerificationConfirmView(APIView):

    @swagger_auto_schema(
        tags=['auth'], operation_description="Phone Verification Confirmation",
        request_body=PhoneVerificationConfirmSerializer(), responses={200: 'Success'}
    )
    def post(self, request):
        serializer = PhoneVerificationConfirmSerializer(data=request.data, context={'user': self.request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(
        tags=['auth'], operation_description="Reset Password", request_body=PasswordResetSerializer(),
        responses={200: 'Success'}
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class ResetPasswordConfirmView(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(
        tags=['auth'], operation_description="Reset Password Confirmation",
        request_body=PasswordResetConfirmSerializer(), responses={200: 'Success'}
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(tags=['auth'])
    def post(self, request):
        return super().post(request)


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (IsOwnerUserProfile, )
