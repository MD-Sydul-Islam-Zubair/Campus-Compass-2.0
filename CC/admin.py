from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile

# Register your models here.

@admin.register(Circular)
class CircularAdmin(admin.ModelAdmin):
    list_display = ('title', 'institute', 'admission_period', 'published_date', 'is_active')
    list_filter = ('institute', 'is_active')
    search_fields = ('title', 'institute__title', 'programs')
    date_hierarchy = 'published_date'
    list_per_page = 20
    fieldsets = (
        ('Basic Information', {'fields': ('institute', 'title', 'image')}),
        ('Details', {'fields': ('admission_period', 'programs', 'details')}),
        ('Status', {'fields': ('is_active',)}),
    )

# Register other models

User = get_user_model()

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')  # Add any additional required fields

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    max_num = 1

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ()}),  # Add any custom fields here
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)

admin.site.register([Category, InstituteInfo, InstituteImage])