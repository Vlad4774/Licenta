from django import forms
from .models import Product, Category, Customer, Location, Project, Item, Contract, CustomUser
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'short_description', 'description', 'category']

    short_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'customer', 'acquisition_status', 'acquisition_probability', 'dos', 'sop', 'eop', 'products']
        widgets = {
            'dos': forms.DateInput(attrs={'type': 'date'}),
            'sop': forms.DateInput(attrs={'type': 'date'}),
            'eop': forms.DateInput(attrs={'type': 'date'}),
            'acquisition_probability': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 0.01}),
            'products': forms.SelectMultiple(attrs={'size': 5}),
        }

class ItemForm(forms.ModelForm):
    schedule_years = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=5,
        help_text="Select the number of years for the schedule plan."
    )

    class Meta:
        model = Item
        fields = ['product', 'location', 'schedule_years']

class CategoryRequestForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class CustomerRequestForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'address']


class LocationRequestForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['address', 'city', 'country']

class ContractUploadForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['file']
      
User = get_user_model()      

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Name', required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'email', 'password1', 'password2', 'profile_picture']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Un cont cu acest email există deja.")
        return email
    
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'email', 'profile_picture']