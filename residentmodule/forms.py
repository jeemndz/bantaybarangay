from django import forms
from .models import Resident


class ResidentForm(forms.ModelForm):

    class Meta:
        model = Resident

        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'suffix',
            'gender',
            'birth_date',
            'address',
            'contact_number',
            'email',
        ]

        widgets = {

            'first_name': forms.TextInput(attrs={
                'placeholder': 'Enter first name',
            }),

            'middle_name': forms.TextInput(attrs={
                'placeholder': 'Enter middle name',
            }),

            'last_name': forms.TextInput(attrs={
                'placeholder': 'Enter last name',
            }),

            'suffix': forms.TextInput(attrs={
                'placeholder': 'Jr., Sr., III',
            }),

            'gender': forms.Select(),

            'birth_date': forms.DateInput(attrs={
                'type': 'date',
            }),

            'address': forms.Textarea(attrs={
                'placeholder': 'Enter complete address',
                'rows': 4,
            }),

            'contact_number': forms.TextInput(attrs={
                'placeholder': '09XXXXXXXXX',
            }),

            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter email address',
            }),
        }