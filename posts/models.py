from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    POST_TYPES = (
        ('psa', 'PSA'),
        ('poll', 'Poll'),
        ('meme', 'Meme'),
        ('repost', 'Repost'),
        ('article', 'Article'),
    )
    slug = models.SlugField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=30)
    comments = models.PositiveIntegerField(default=0, editable=False)
    upvotes = models.PositiveIntegerField(default=0, editable=False)
    upvoters = models.ManyToManyField(User, related_name='upvoted_posts')
    type = models.CharField(max_length=10, choices=POST_TYPES)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return '%d' % self.id


class Poll(models.Model):
    question = models.CharField(max_length=255)
    votes = models.PositiveIntegerField(default=0, editable=False)
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.question


class Choice(models.Model):
    choice_text = models.CharField(max_length=200)
    votes = models.PositiveIntegerField(default=0, editable=False)
    voters = models.ManyToManyField(User, related_name='voted_choices')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices')

    def __str__(self):
        return self.choice_text


class Meme(models.Model):
    image = models.ImageField(upload_to='posts/memes')
    title = models.CharField(max_length=100, null=True, blank=True)
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    def __str__(self):
        return '%d' % self.id


class Article(models.Model):
    VIDEO_TYPES = (
        ('vimeo', 'Vimeo'),
        ('youtube', 'Youtube'),
    )
    title = models.CharField(max_length=100)
    video = models.URLField(null=True, blank=True)
    video_id = models.CharField(max_length=15, null=True, blank=True)
    thumbnail = models.URLField(null=True, blank=True)
    video_type = models.CharField(max_length=10, choices=VIDEO_TYPES, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='posts/articles')
    text = models.TextField(null=True, blank=True)
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    def __str__(self):
        return '%d' % self.id


class PSA(models.Model):
    text = models.TextField()
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    def __str__(self):
        return '%d' % self.id


class Repost(models.Model):
    url = models.URLField()
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    def __str__(self):
        return '%d' % self.id


class Comment(models.Model):
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return '%d' % self.id
