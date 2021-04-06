from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    text = models.TextField()
    ethics = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    trust = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    accuracy = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    fairness = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    contribution = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    expertise = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    rating = models.FloatField(blank=True, null=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_reviews')
    agreed = models.ManyToManyField(User, related_name='agreed', blank=True)
    disagreed = models.ManyToManyField(User, related_name='disagreed', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%d' % self.id


class Reply(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.OneToOneField(Review, on_delete=models.CASCADE)
    agreed = models.ManyToManyField(User, related_name='response_agreed', blank=True)
    disagreed = models.ManyToManyField(User, related_name='response_disagreed', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = 'Replies'

    def __str__(self):
        return '%d' % self.id
