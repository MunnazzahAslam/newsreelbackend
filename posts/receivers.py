from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .models import Post, Comment
from utils.onesignal_client import send_notification


FRONTEND_DOMAIN = settings.FRONTEND_DOMAIN


@receiver(post_save, sender=Post)
def notify_followers(sender, created, instance, **kwargs):
    if created:
        author = instance.author
        followers = list(author.followers.all().values_list('user_id', flat=True))
        post_url = '%s/post/%d' % (FRONTEND_DOMAIN, instance.id)
        content = 'New post by %s' % author.username
        notification_body = {
            "url": post_url,
            "headings": {"en": "NewsReel"},
            'contents': {'en': content},
            'include_external_user_ids': followers,
        }
        send_notification(notification_body)


@receiver(post_save, sender=Post)
def increase_posts_number(sender, created, instance, **kwargs):
    if created:
        user = instance.author
        user.posts += 1
        user.save()


@receiver(post_delete, sender=Post)
def decrease_posts_number(sender, instance, **kwargs):
    user = instance.author
    if user.posts:
        user.posts -= 1
        user.save()


@receiver(post_save, sender=Comment)
def increase_comments_number(sender, created, instance, **kwargs):
    if created:
        post = instance.post
        post.comments += 1
        post.save()

        comment_author = instance.author
        if post.author != comment_author:
            comment_author.comments += 1
            comment_author.save()


@receiver(post_delete, sender=Comment)
def decrease_comments_number(sender, instance, **kwargs):
    post = instance.post
    post.comments -= 1
    post.save()

    comment_author = instance.author
    if post.author != comment_author and comment_author.comments:
        comment_author.comments -= 1
        comment_author.save()
