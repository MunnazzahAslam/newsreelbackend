from django.urls import path

from .views import FollowingsView


urlpatterns = [
    path('followings/<int:pk>/', FollowingsView.as_view()),
]
