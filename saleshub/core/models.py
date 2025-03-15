from django.db import models
from django.contrib.auth.models import User

from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Location(models.Model):
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.city}, {self.country}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    short_description = models.CharField(max_length=500)
    description = models.TextField() 
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sold_to = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Project(models.Model):
    ACQUISITION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    name = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    acquisition_status = models.CharField(max_length=20, choices=ACQUISITION_STATUS_CHOICES, default='pending')
    acquisition_probability = models.DecimalField(max_digits=5, decimal_places=2)
    dos = models.DateField(verbose_name="Date of Start")
    sop = models.DateField(verbose_name="Start of Production")
    eop = models.DateField(verbose_name="End of Production")
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, default=1)
    products = models.ManyToManyField('Product', related_name='projects', blank=True)

    def __str__(self):
        return f"{self.name} ({self.customer.name})"
    

class Item(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    schedule_years = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.product.name} for {self.project.name} in {self.location}"

class Volume(models.Model):
    item = models.ForeignKey(Item, related_name='volumes', on_delete=models.CASCADE)
    year = models.IntegerField()  
    min_volume = models.FloatField(null=True, blank=True)
    expected_volume = models.FloatField(null=True, blank=True)
    max_volume = models.FloatField(null=True, blank=True)

class Pricing(models.Model):
    item = models.ForeignKey(Item, related_name='pricing', on_delete=models.CASCADE)
    year = models.IntegerField() 
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    packaging_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transport_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warehouse_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class Cost(models.Model):
    item = models.ForeignKey(Item, related_name='costs', on_delete=models.CASCADE)
    year = models.IntegerField() 
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    material_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    overhead_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)