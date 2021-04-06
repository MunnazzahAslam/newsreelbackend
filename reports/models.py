from django.db import models
from django.contrib.auth import get_user_model

from posts.models import Post
from reviews.models import Review, Reply

User = get_user_model()


class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, blank=True, null=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, blank=True, null=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='reports', null=True)

    def __str__(self):
        return '%d' % self.id
