from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFollowing(models.Model):
    user = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'following_user')
