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