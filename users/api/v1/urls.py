from django.urls import path

from .views import (
    LoginView,
    SignupView,
    PhoneVerificationView,
    PhoneVerificationConfirmView,
    ResetPasswordView,
    ResetPasswordConfirmView,
    UserDetailView,
    LogoutApiView,
    CustomTokenRefreshView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', LogoutApiView.as_view(), name='logout'),
    path('phone/verification/', PhoneVerificationView.as_view(), name='phone_verification'),
    path('phone/verification/confirm/', PhoneVerificationConfirmView.as_view(), name='phone_verification_confirm'),
    path('password/reset/', ResetPasswordView.as_view(), name='reset_password'),
    path('password/reset/confirm/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='refresh_token'),
    path('users/<int:pk>/', UserDetailView.as_view()),
]
