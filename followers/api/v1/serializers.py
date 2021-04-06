from rest_framework import serializers

from followers.models import UserFollowing


class UserFollowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFollowing
        fields = ('id', 'following_user')
        read_only_fields = ('id', )

    def validate(self, data):
        user = self.context['request'].user
        following_user = data['following_user']

        if user == following_user:
            raise serializers.ValidationError({'error': 'cannot follow himself'})

        if UserFollowing.objects.filter(user=user, following_user=following_user).exists():
            raise serializers.ValidationError({'error': 'have already following'})

        data['user'] = user
        return data
