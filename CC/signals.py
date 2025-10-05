# In your signals.py or models.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


from django.contrib.auth import get_user_model
from .models import Notification, Bookmark, Circular, InstituteInfo

User = get_user_model()

@receiver(post_save, sender=Circular)
def notify_bookmarked_users_new_circular(sender, instance, created, **kwargs):
    if created:  # Only for new circulars
        institute = instance.institute
        bookmarked_users = Bookmark.objects.filter(institute=institute).select_related('user')
        
        for bookmark in bookmarked_users:
            Notification.objects.create(
                user=bookmark.user,
                institute=institute,
                circular=instance,
                message=f"New circular posted for {institute.title}: {instance.title}",
                notification_type='new_circular'
            )

@receiver(post_save, sender=InstituteInfo)
def notify_bookmarked_users_institute_update(sender, instance, created, **kwargs):
    if not created:  # Only for updates, not new creations
        bookmarked_users = Bookmark.objects.filter(institute=instance).select_related('user')
        
        for bookmark in bookmarked_users:
            Notification.objects.create(
                user=bookmark.user,
                institute=instance,
                message=f"Updates made to {instance.title}",
                notification_type='institute_update'
            )

@receiver(post_save, sender=Circular)
def notify_bookmarked_users_circular_update(sender, instance, created, **kwargs):
    if not created:  # Only for updates, not new circulars
        institute = instance.institute
        bookmarked_users = Bookmark.objects.filter(institute=institute).select_related('user')
        
        for bookmark in bookmarked_users:
            Notification.objects.create(
                user=bookmark.user,
                institute=institute,
                circular=instance,
                message=f"Circular updated for {institute.title}: {instance.title}",
                notification_type='circular_update'
            )    