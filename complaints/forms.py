from django import forms
from .models import Complaint


class ComplaintForm(forms.ModelForm):

    class Meta:
        model = Complaint

        fields = [
            'resident_id',
            'complaint_type',
            'subject',
            'description',
            'location',
            'incident_date',
            'priority',
            'status',
        ]

        widgets = {

            'resident_id': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter resident ID'
            }),

            'complaint_type': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Example: Property Dispute'
            }),

            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter complaint subject'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Describe the complaint...',
                'rows': 5
            }),

            'location': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Enter incident location',
                'rows': 3
            }),

            'incident_date': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local'
            }),

            'priority': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter priority'
            }),

            'status': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter status'
            }),
        }