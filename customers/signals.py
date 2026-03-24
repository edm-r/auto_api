from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile, WishList


User = get_user_model()


@receiver(post_save, sender=User)
def create_customer_models(sender, instance, created, **kwargs):
    if not created:
        return
    UserProfile.objects.get_or_create(user=instance)
    WishList.objects.get_or_create(user=instance)

