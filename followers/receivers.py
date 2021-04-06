from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .models import UserFollowing


@receiver(post_save, sender=UserFollowing)
def increase_subscribers_number(sender, created, instance, **kwargs):
    user = instance.following_user
    if created:
        user.subscribers += 1

    user.save()


@receiver(post_delete, sender=UserFollowing)
def decrease_subscribers_number(sender, instance, **kwargs):
    user = instance.following_user
    user.subscribers -= 1
    user.save()
