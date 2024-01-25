from .models import CustomUser
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction

@receiver(post_save, sender=AbstractUser)
def post_save_create_profile(sender, instance, created, *args, **kwargs):
    if created:
        CustomUser.objects.create(user=instance)


@receiver(post_save, sender=Transaction)
def update_balance(sender, instance, created, **kwargs):
    if not created and instance.status == 'approved':
        user = instance.user
        user.balance += instance.amount
        user.save()