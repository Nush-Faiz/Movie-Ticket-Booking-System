from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email, RegexValidator
from .models import UserProfile

class ExtendedUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, validators=[validate_email],widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(
        max_length=15,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Phone number must be 10 digits',
                code='invalid_phone'
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    full_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                phone=self.cleaned_data['phone']
            )
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone']
        widgets = {
            'phone': forms.TextInput(attrs={'pattern': '[0-9]{10}'})
        }