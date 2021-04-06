from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete

from .models import Review


@receiver(pre_save, sender=Review)
def calculate_rating(sender, instance, *args, **kwargs):
    instance.rating = round((instance.ethics + instance.trust + instance.accuracy +
                             instance.fairness + instance.contribution + instance.expertise) / 6, 2)


def update_user_stats(user):
    stats = Review.objects.filter(user=user).aggregate(
        ethics=models.Avg('ethics'), trust=models.Avg('trust'), accuracy=models.Avg('accuracy'),
        fairness=models.Avg('fairness'), contribution=models.Avg('contribution'), expertise=models.Avg('expertise'),
        rating=models.Avg('rating')
    )

    for key, value in stats.items():
        if value:
            setattr(user, key, round(value, 2))
        else:
            setattr(user, key, 0)

    user.save()


@receiver(post_save, sender=Review)
def post_save_callback(sender, created, instance, **kwargs):
    user = instance.user
    author = instance.author
    if created:
        user.own_reviews += 1
        author.reviews += 1
        author.save()

    update_user_stats(user)


@receiver(post_delete, sender=Review)
def post_delete_callback(sender, instance, **kwargs):
    author = instance.author
    if author.reviews:
        author.reviews -= 1
        author.save()

    user = instance.user
    if user.own_reviews:
        user.own_reviews -= 1

    update_user_stats(user)
