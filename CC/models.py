from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class InstituteInfo(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  
    description = models.TextField()
    location = models.CharField(max_length=100)
    nearby_hostels = models.CharField(max_length=100)
    rank = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    contact = models.TextField()
    status_choices = (
        ('Closed', 'Closed'),
        ('Apply', 'Apply')
    )
    status = models.CharField(max_length=50, choices=status_choices, default='Closed')

    def __str__(self):
        return self.title

class InstituteImage(models.Model):
    institute = models.ForeignKey(InstituteInfo, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='institutes/')

    def __str__(self):
        return f"Image for {self.institute.title}"
    


class Circular(models.Model):
    institute = models.ForeignKey(InstituteInfo, on_delete=models.CASCADE, related_name='circulars')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='circulars/')
    admission_period = models.CharField(max_length=100, default="Fall 2024")   
    programs = models.TextField( default="Undergraduation")
    details = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)  # Add this field

    def __str__(self):
        return f"{self.title} - {self.institute.title}"



class CustomUser(AbstractUser):
    # Add any custom fields here
    
    # Fix the related_name clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="customuser_groups",  # Changed from default
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_permissions",  # Changed from default
        related_query_name="customuser",
    )

    class Meta:
        db_table = 'custom_user'  # Custom table name to avoid clash
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

User = get_user_model()
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)   # Changed from User to CustomUser
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True,validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    bio = models.TextField(max_length=500, blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'"
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )
    birth_date = models.DateField(null=True, blank=True)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def get_full_address(self):
        return f"{self.address}, {self.city}, {self.country}"

    class Meta:
        verbose_name_plural = "Profiles"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile for new users"""
    if created:
        from .models import Profile  # Import here to avoid circular imports
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile when user is saved"""
    instance.profile.save()
