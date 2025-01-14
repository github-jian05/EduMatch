from django import forms
from .models import Commission


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = ['title', 'description', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter commission title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the commission...'}),
        }
