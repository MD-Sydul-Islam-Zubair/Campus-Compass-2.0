from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile
from .models import*
from django.forms import ModelForm

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import BlogPost, BlogComment

User = get_user_model()

# forms.py


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Let signals handle profile creation
        return user    


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'bio', 'birth_date', 'gender', 
                 'phone_number', 'address', 'city', 'country',
                 'website', 'twitter', 'facebook', 'instagram', 'linkedin']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional
        for field in self.fields:
            self.fields[field].required = False
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number == '':
            return None
        return phone_number
    
class InstitiutionForm(ModelForm):
    class Meta:
        model = InstituteInfo
        fields = '__all__'



class InstituteForm(ModelForm):
    class Meta:
        model = InstituteInfo
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'contact': forms.Textarea(attrs={'rows': 3}),
        }

# Remove the custom file field and handle images separately in the view
class InstituteForm(forms.ModelForm):
    class Meta:
        model = InstituteInfo
        fields = ['title', 'category', 'description', 'location', 'rank', 'department', 'contact', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'contact': forms.Textarea(attrs={'rows': 3}),
        }
        
class CircularForm(ModelForm):
    class Meta:
        model = Circular
        exclude = ['published_date']  # This field will be handled automatically
        widgets = {
            'details': forms.Textarea(attrs={'rows': 4}),
            'programs': forms.Textarea(attrs={'rows': 3}),
        }      


class HostelForm(forms.ModelForm):
    # Remove the custom file field and handle images separately in the view
    class Meta:
        model = Hostel
        fields = ['name', 'location', 'distance_from_institute', 'contact_info', 
                 'rent_range', 'amenities', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'amenities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'WiFi, Laundry, Food, Security, etc.'}),
            'contact_info': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text to fields
        self.fields['distance_from_institute'].help_text = 'e.g., 0.5 km, 10 min walk'
        self.fields['rent_range'].help_text = 'e.g.,  ৳5000- ৳8000/month'
        self.fields['amenities'].help_text = 'List amenities separated by commas'




     
# ================================
#            Blogpost
# ================================


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter post title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Share your experience or advice...'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., study tips, admission, campus life'}),
        }

class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your comment...'}),
        }      