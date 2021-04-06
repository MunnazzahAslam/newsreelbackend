import os

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField

from phonenumber_field.modelfields import PhoneNumberField


def get_avatar_path(instance, filename):
    return os.path.join(
        'avatars',
        str(instance.id),
        filename
    )


def get_avatar_thumbnail_path(instance, filename):
    return os.path.join(
        'avatars',
        str(instance.id),
        'thumbnail_' + filename
    )


class User(AbstractUser):
    first_name = None
    last_name = None
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    avatar = models.ImageField(upload_to=get_avatar_path)
    avatar_thumbnail = ProcessedImageField(
        upload_to=get_avatar_thumbnail_path,
        processors=[ResizeToFill(45, 45)],
        format='JPEG',
        options={'quality': 60},
        null=True
    )
    phone_number = PhoneNumberField(
        unique=True,
        error_messages={
            'unique': _("A user with that phone number already exists."),
        },
    )
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    bio = models.CharField(max_length=300, blank=True, null=True)

    # Statistics
    posts = models.PositiveIntegerField(_('Number of posts'), default=0, editable=False)
    own_reviews = models.PositiveIntegerField(_('Number of personal reviews'), default=0, editable=False)
    reviews = models.PositiveIntegerField(_('Number of reviews'), default=0, editable=False)
    comments = models.PositiveIntegerField(_('Number of comments'), default=0, editable=False)
    subscribers = models.PositiveIntegerField(_('Number of subscribers'), default=0, editable=False)
    rating = models.FloatField(_('Average rating'), default=0, editable=False)
    ethics = models.FloatField(default=0, editable=False)
    trust = models.FloatField(default=0, editable=False)
    accuracy = models.FloatField(default=0, editable=False)
    fairness = models.FloatField(default=0, editable=False)
    contribution = models.FloatField(default=0, editable=False)
    expertise = models.FloatField(default=0, editable=False)

    is_top_rated = models.BooleanField(default=False)
    is_verified_phone_number = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email']

    def __str__(self):
        return self.email


class PhoneVerification(models.Model):
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email
