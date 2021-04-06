from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import status, views
from rest_framework.response import Response

from followers.models import UserFollowing
from .serializers import UserFollowingSerializer

User = get_user_model()


class FollowingsView(views.APIView):

    def post(self, request, pk):
        following_user = get_object_or_404(User, pk=pk)
        serializer = UserFollowingSerializer(data={'following_user': following_user.id}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, pk):
        following_user = get_object_or_404(User, pk=pk)
        UserFollowing.objects.filter(following_user=following_user, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
