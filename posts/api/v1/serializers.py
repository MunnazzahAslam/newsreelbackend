import requests
import urllib.parse as urlparse

from django.utils.text import slugify

from rest_framework import serializers

from users.api.v1.serializers import UserSerializer
from posts.models import Poll, Choice, Meme, Article, PSA, Repost, Post, Comment


class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Choice
        fields = ('id', 'choice_text')
        read_only_fields = ('id',)


class ChoiceDetailSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    is_voted = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ('id', 'choice_text', 'votes', 'is_voted')
        read_only_fields = ('id', 'votes')

    def get_is_voted(self, obj):
        user_id = self.context['request'].user.id
        return obj.voters.filter(id=user_id).exists()

    def get_votes(self, obj):
        total_votes = self.context['total_votes']
        vote_percent = int(obj.votes / total_votes * 100) if total_votes else 0
        return vote_percent


class ChoiceVoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Choice
        fields = ('id',)
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if not instance.voters.filter(id=user.id).exists():
            poll = instance.poll
            poll.votes += 1
            poll.save()
            instance.votes += 1
            instance.voters.add(user)
            instance.save()

        return instance


class PollSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()
    category = serializers.CharField(max_length=30, write_only=True)
    choices_text = serializers.ListField(child=serializers.CharField(), min_length=2, max_length=5, write_only=True)

    class Meta:
        model = Poll
        fields = ('question', 'category', 'votes', 'choices', 'choices_text')

    def get_choices(self, obj):
        request = self.context['request']
        user_id = request.user.id
        choices = obj.choices.all()
        if user_id and choices.filter(voters=user_id).exists():
            serializer = ChoiceDetailSerializer(choices, many=True, context={
                'request': request,
                'total_votes': obj.votes
            })
            data = serializer.data

            max_votes = 0
            max_votes_choice = None
            total_votes_percent = 0
            for choice in data:
                votes = choice['votes']
                if votes > max_votes:
                    max_votes = votes
                    max_votes_choice = choice

                total_votes_percent += votes

            if total_votes_percent != 100:
                max_votes_choice['votes'] += 1
        else:
            serializer = ChoiceSerializer(choices, many=True, context={'request': request})
            data = serializer.data

        return data

    def create(self, validated_data):
        author = self.context['request'].user
        category = validated_data.pop('category')
        post = Post.objects.create(author=author, type='poll', category=category)
        question = validated_data['question']
        slug = '%s %d' % (question, post.id)
        post.slug = slugify(slug)
        post.save()

        choices = validated_data.pop('choices_text')
        poll = Poll.objects.create(post=post, **validated_data)

        for choice in choices:
            Choice.objects.create(poll=poll, choice_text=choice)

        return poll


class MemeSerializer(serializers.ModelSerializer):
    category = serializers.CharField(max_length=30, write_only=True)

    class Meta:
        model = Meme
        fields = ('title', 'category', 'image')

    def create(self, validated_data):
        author = self.context['request'].user
        category = validated_data.pop('category')
        post = Post.objects.create(author=author, type='meme', category=category)
        username = author.username
        slug = '%s %s %d' % (username, post.type, post.id)
        post.slug = slugify(slug)
        post.save()

        return Meme.objects.create(post=post, **validated_data)


class ArticleSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(max_length=70, write_only=True, required=False)
    category = serializers.CharField(max_length=30, write_only=True, required=False)

    class Meta:
        model = Article
        fields = ('title', 'category', 'slug', 'video', 'video_id', 'thumbnail', 'video_type', 'image', 'text')
        read_only_fields = ('thumbnail', 'video_id', 'video_type')

    def validate_video(self, video):
        if not video.startswith('https://vimeo.com') and not video.startswith('https://www.youtube.com'):
            raise serializers.ValidationError('Youtube or vimeo video are supported')

        return video

    def validate(self, attrs):
        video = attrs.get('video')
        image = attrs.get('image')
        if not video and not image and self.instance:
            image = self.instance.image

        if image and video:
            raise serializers.ValidationError({'error': 'Include image or video'})

        if not image and not video:
            raise serializers.ValidationError({'error': 'Image or video is required'})

        if video:
            parsed = urlparse.urlparse(video)
            if 'vimeo' in video:
                attrs['video_type'] = 'vimeo'
                video_id = parsed.path.split('/')[1]
                url = 'https://vimeo.com/api/v2/video/%s.json' % video_id
                response = requests.get(url)
                if response.status_code != 200:
                    raise serializers.ValidationError({'video': 'Incorrect vimeo link'})

                thumbnail = response.json()[0]['thumbnail_large']
                if thumbnail.startswith('http://'):
                    thumbnail = thumbnail.replace('http', 'https')

                attrs['thumbnail'] = thumbnail
            else:
                attrs['video_type'] = 'youtube'
                query_params = urlparse.parse_qs(parsed.query)
                if 'v' not in query_params:
                    raise serializers.ValidationError({'video': 'Incorrect youtube link'})

                video_id = query_params['v'][0]
                attrs['thumbnail'] = 'https://img.youtube.com/vi/%s/0.jpg' % video_id

            attrs['video_id'] = video_id
        else:
            text = attrs.get('text')
            if not text:
                raise serializers.ValidationError({'text': 'This field is required.'})

        return attrs

    def create(self, validated_data):
        author = self.context['request'].user
        if 'category' not in validated_data:
            raise serializers.ValidationError({'category': 'This field is required.'})

        if 'slug' not in validated_data:
            raise serializers.ValidationError({'slug': 'This field is required.'})

        slug = validated_data.pop('slug')
        category = validated_data.pop('category')
        post = Post.objects.create(author=author, type='article', category=category)
        slug = '%s-%d' % (slug, post.id)
        post.slug = slugify(slug)
        post.save()

        return Article.objects.create(post=post, **validated_data)

    def update(self, instance, validated_data):
        video = validated_data.get('video')
        image = validated_data.get('image')
        if image and instance.video:
            instance.video = None
            instance.video_id = None
            instance.thumbnail = None
            instance.video_type = None
        elif video and instance.image:
            instance.image.delete()

        return super().update(instance, validated_data)


class PSASerializer(serializers.ModelSerializer):
    slug = serializers.CharField(max_length=70, write_only=True, required=False)
    category = serializers.CharField(max_length=30, write_only=True, required=False)

    class Meta:
        model = PSA
        fields = ('text', 'category', 'slug')

    def create(self, validated_data):
        author = self.context['request'].user
        if 'category' not in validated_data:
            raise serializers.ValidationError({'category': 'This field is required.'})

        if 'slug' not in validated_data:
            raise serializers.ValidationError({'slug': 'This field is required.'})

        slug = validated_data.pop('slug')
        category = validated_data.pop('category')
        post = Post.objects.create(author=author, type='psa', category=category)
        slug = '%s-%d' % (slug, post.id)
        post.slug = slugify(slug)
        post.save()

        return PSA.objects.create(post=post, **validated_data)


class RepostSerializer(serializers.ModelSerializer):
    category = serializers.CharField(max_length=30, write_only=True)

    class Meta:
        model = Repost
        fields = ('url', 'category')

    def validate_url(self, url):
        if 'twitter.com' not in url:
            raise serializers.ValidationError('Twitter url is allowed')

        return url

    def create(self, validated_data):
        author = self.context['request'].user
        category = validated_data.pop('category')
        post = Post.objects.create(author=author, type='repost', category=category)
        username = author.username
        slug = '%s %s %d' % (username, post.type, post.id)
        post.slug = slugify(slug)
        post.save()

        return Repost.objects.create(post=post, **validated_data)


class PostSerializer(serializers.ModelSerializer):
    psa = PSASerializer(read_only=True)
    poll = PollSerializer(read_only=True)
    meme = MemeSerializer(read_only=True)
    author = UserSerializer(read_only=True)
    repost = RepostSerializer(read_only=True)
    article = ArticleSerializer(read_only=True)
    text = serializers.CharField(required=False, allow_null=True, write_only=True)
    title = serializers.CharField(required=False, write_only=True)
    video = serializers.URLField(required=False, allow_null=True, write_only=True)
    image = serializers.ImageField(required=False, allow_null=True, write_only=True)
    is_upvoted = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'comments', 'type', 'category', 'slug', 'psa', 'poll', 'meme', 'repost', 'article', 'author',
                  'upvotes', 'is_upvoted', 'text', 'title', 'video', 'image', 'created_at')
        read_only_fields = ('id', 'comments', 'type', 'slug', 'upvotes', 'created_at')

    def get_is_upvoted(self, obj):
        user_id = self.context['request'].user.id
        return obj.upvoters.filter(id=user_id).exists()

    def to_representation(self, instance):
        ret = super(PostSerializer, self).to_representation(instance)
        for post_types_info in Post.POST_TYPES:
            post_type = post_types_info[0]
            if post_type in ret and ret[post_type]:
                data = ret.pop(post_type)
                ret.update(data)
            elif post_type in ret:
                del ret[post_type]

        return ret

    def update(self, instance, validated_data):
        category = validated_data.pop('category')
        if instance.type == 'psa':
            serializer = PSASerializer(instance=instance.psa, data=validated_data, partial=True)
        else:
            serializer = ArticleSerializer(instance=instance.article, data=validated_data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        instance.category = category
        instance.save()
        return instance


class PostUpVoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id',)
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if not instance.upvoters.filter(id=user.id).exists():
            instance.upvotes += 1
            instance.upvoters.add(user)
            instance.save()

        return instance


class RelatedPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    article = ArticleSerializer(read_only=True)
    is_upvoted = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'comments', 'type', 'category', 'slug', 'article', 'author', 'upvotes', 'is_upvoted',
                  'created_at')
        read_only_fields = ('id', 'comments', 'type', 'category', 'slug', 'upvotes', 'created_at')

    def get_is_upvoted(self, obj):
        user_id = self.context['request'].user.id
        return obj.upvoters.filter(id=user_id).exists()

    def to_representation(self, instance):
        ret = super(RelatedPostSerializer, self).to_representation(instance)
        data = ret.pop('article')
        ret.update(data)
        return ret


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'post', 'parent_comment', 'author', 'created_at')
        read_only_fields = ('id', 'created_at')
        extra_kwargs = {
            'post': {'write_only': True},
            'parent_comment': {'write_only': True}
        }

    def create(self, validated_data):
        author = self.context['request'].user
        comment = Comment.objects.create(author=author, **validated_data)
        return comment
