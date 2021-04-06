from rest_framework import serializers

from reviews.models import Review, Reply
from users.api.v1.serializers import UserSerializer


class ReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    agreed_num = serializers.SerializerMethodField()
    disagreed_num = serializers.SerializerMethodField()
    is_agreed = serializers.SerializerMethodField()
    is_disagreed = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ('id', 'text', 'user', 'review', 'agreed_num', 'disagreed_num', 'is_agreed', 'is_disagreed',
                  'created_at')
        read_only_fields = ('id', 'created_at')

    def get_agreed_num(self, obj):
        return obj.agreed.all().count()

    def get_disagreed_num(self, obj):
        return obj.disagreed.all().count()

    def get_is_agreed(self, obj):
        user_id = self.context['request'].user.id
        return obj.agreed.filter(id=user_id).exists()

    def get_is_disagreed(self, obj):
        user_id = self.context['request'].user.id
        return obj.disagreed.filter(id=user_id).exists()

    def create(self, validated_data):
        user = self.context['request'].user
        return Reply.objects.create(user=user, **validated_data)


class ReviewDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    reply = ReplySerializer(read_only=True)
    rating = serializers.ReadOnlyField()
    agreed_num = serializers.SerializerMethodField()
    disagreed_num = serializers.SerializerMethodField()
    is_agreed = serializers.SerializerMethodField()
    is_disagreed = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'text', 'ethics', 'trust', 'accuracy', 'fairness', 'contribution', 'expertise', 'rating',
                  'reply', 'user', 'author', 'agreed_num', 'disagreed_num', 'is_agreed', 'is_disagreed', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_agreed_num(self, obj):
        return obj.agreed.all().count()

    def get_disagreed_num(self, obj):
        return obj.disagreed.all().count()

    def get_is_agreed(self, obj):
        user_id = self.context['request'].user.id
        return obj.agreed.filter(id=user_id).exists()

    def get_is_disagreed(self, obj):
        user_id = self.context['request'].user.id
        return obj.disagreed.filter(id=user_id).exists()

    def validate_user(self, user):
        author = self.context['request'].user
        if user == author:
            raise serializers.ValidationError('Cannot review yourself')

        if Review.objects.filter(author_id=author.id, user_id=user.id).exists():
            raise serializers.ValidationError('You have already reviewed')

        return user

    def create(self, validated_data):
        user = self.context['request'].user
        return Review.objects.create(author=user, **validated_data)


class VoteSerializer(serializers.Serializer):
    vote = serializers.BooleanField()

    def update(self, instance, validated_data):
        user = self.context['request'].user
        vote = validated_data['vote']
        if vote:
            instance.agreed.add(user)
            instance.disagreed.remove(user)
        else:
            instance.agreed.remove(user)
            instance.disagreed.add(user)

        instance.save()
        return instance
