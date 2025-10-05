from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator, FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class InstituteInfo(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    location = models.CharField(max_length=100)
    # REMOVE THIS LINE: nearby_hostels = models.CharField(max_length=100)
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
    programs = models.TextField(default="Undergraduation")
    details = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.title} - {self.institute.title}"

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="customuser_groups",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_permissions",
        related_query_name="customuser",
    )

    class Meta:
        db_table = 'custom_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True,
                                    validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    bio = models.TextField(max_length=500, blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'"
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
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


# ---------- FIXED SIGNAL ----------


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile for new users automatically."""
    if created:
        Profile.objects.create(user=instance)


class Comment(models.Model):
    institute = models.ForeignKey(InstituteInfo, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user.username} on {self.institute.title}"
    

# Add this to your models.py after the Comment model
class Bookmark(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    institute = models.ForeignKey(InstituteInfo, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'institute')  # Prevent duplicate bookmarks
        verbose_name_plural = "Bookmarks"

    def __str__(self):
        return f"{self.user.username} bookmarked {self.institute.title}"
    

class Hostel(models.Model):
    name = models.CharField(max_length=200)
    institute = models.ForeignKey(InstituteInfo, on_delete=models.CASCADE, related_name="nearby_hostels")
    location = models.CharField(max_length=200)
    distance_from_institute = models.CharField(max_length=100, help_text="e.g., 0.5 km, 10 min walk")
    contact_info = models.TextField()
    rent_range = models.CharField(max_length=100, help_text="e.g., ₹5000-₹8000/month")
    amenities = models.TextField(help_text="Comma-separated amenities")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Hostels"
        ordering = ['distance_from_institute']

    def __str__(self):
        return f"{self.name} near {self.institute.title}"

class HostelImage(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='hostels/')
    
    def __str__(self):
        return f"Image for {self.hostel.name}"