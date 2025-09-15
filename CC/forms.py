from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile
from .models import*
from django.forms import ModelForm

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

# forms.py
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
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
    
    def clean_profile_pic(self):
        profile_pic = self.cleaned_data.get('profile_pic')
        if profile_pic:
            # Check file size
            if profile_pic.size > 2*1024*1024:  # 2MB limit
                raise forms.ValidationError("Image file too large ( > 2MB )")
            
            # Check content type
            if hasattr(profile_pic, 'file') and hasattr(profile_pic.file, 'content_type'):
                content_type = profile_pic.file.content_type
                if content_type not in ['image/jpeg', 'image/png']:
                    raise forms.ValidationError("Only JPEG or PNG images allowed")
            else:
                # Handle case where the file doesn't have content_type
                # You might want to check the file extension instead
                name = profile_pic.name.lower()
                if not name.endswith(('.jpg', '.jpeg', '.png')):
                    raise forms.ValidationError("Only JPEG or PNG images allowed")
        return profile_pic
    
class InstitiutionForm(ModelForm):
    class Meta:
        model = InstituteInfo
        fields = '__all__'



class InstituteForm(ModelForm):
    class Meta:
        model= InstituteInfo
        fields = '__all__'        

class CircularForm(ModelForm):
    class Meta:
        model= Circular
        fields = '__all__'             