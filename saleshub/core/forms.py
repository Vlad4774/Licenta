from django import forms
from .models import Product, Category, Customer, Location, Project, Item

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'short_description', 'description', 'category', 'sold_to', 'location']

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
    class Meta:
        model = Item
        fields = ['product', 'location']
