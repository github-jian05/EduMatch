from django import forms
from .models import Profile, CustomUser, Commission  # Consolidate imports
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# Registration Form for CustomUser
class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)  # Reference ROLE_CHOICES from CustomUser

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)  # Save the CustomUser instance
        if commit:
            user.save()  # Save CustomUser to database
            role = self.cleaned_data['role']

            # Check if a Profile already exists for the user
            profile, created = Profile.objects.get_or_create(user=user, defaults={'role': role})

            if created:
                print(f"Profile created for user: {user.username}, role: {role}")
            else:
                print(f"Profile updated for user: {user.username}, new role: {role}")
                profile.role = role
                profile.save()

        return user


# Form for creating commissions (already defined)
class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = ['title', 'description', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter commission title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the commission...'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'expertise', 'contact_info', 'profile_picture']

class RoleUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['role']  # Fields to update (e.g., 'role')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Allow updates for username and email




