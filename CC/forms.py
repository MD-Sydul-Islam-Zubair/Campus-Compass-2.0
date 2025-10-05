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
        model= InstituteInfo
        fields = '__all__'        

class CircularForm(ModelForm):
    class Meta:
        model= Circular
        fields = '__all__'             


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
        self.fields['rent_range'].help_text = 'e.g., ₹5000-₹8000/month'
        self.fields['amenities'].help_text = 'List amenities separated by commas'