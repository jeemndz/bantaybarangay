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
            'birth_date',
            'gender',
            'civil_status',

            'house_block_lot',
            'street_purok_sitio',
            'barangay',
            'municipality_city',
            'province',
            'zip_code',

            'contact_number',
            'email',
            'address',
        ]

        widgets = {

            'birth_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'rows': 3
                }
            ),

            'house_block_lot': forms.TextInput(
                attrs={
                    'placeholder': 'House / Block / Lot'
                }
            ),

            'street_purok_sitio': forms.TextInput(
                attrs={
                    'placeholder': 'Street / Purok / Sitio'
                }
            ),

            'barangay': forms.TextInput(
                attrs={
                    'placeholder': 'Barangay'
                }
            ),

            'municipality_city': forms.TextInput(
                attrs={
                    'placeholder': 'Municipality / City'
                }
            ),

            'province': forms.TextInput(
                attrs={
                    'placeholder': 'Province'
                }
            ),

            'zip_code': forms.TextInput(
                attrs={
                    'placeholder': 'ZIP Code'
                }
            ),
        }