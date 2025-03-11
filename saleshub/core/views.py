from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required 
from .models import Product, Pricing, Volume, Cost, Project
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from .forms import ProductForm, ProjectForm

@login_required
def home(request):
    products = Product.objects.all()
    return render(request, 'core/structure/home.html', {'products': products})

def get_started(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'core/structure/get_started.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'core/structure/login.html', {'error': 'Invalid credentials'})
    return render(request, 'core/structure/login.html')

@login_required
def show_products(request):
    products = Product.objects.all()
    return render(request, 'core/product/product_list.html', {'projects': products})


@login_required
def product_detail(request, id):
    product = Product.objects.get(id=id)
    product_data = {
        'name': product.name,
        'short_description': product.short_description,
        'description': product.description,
        'category': product.category.name if product.category else 'N/A', 
        'sold_to': product.sold_to.name if product.sold_to else 'N/A',     
        'location': product.location.name if product.location else 'N/A', 
    }
    volumes = Volume.objects.filter(product=product)
    volume_data = list(volumes.values('year', 'min_volume', 'expected_volume', 'max_volume'))
    prices = Pricing.objects.filter(product=product)
    prices_data = list(prices.values('year', 'base_price', 'packaging_price', 'transport_price', 'warehouse_price'))
    costs = Cost.objects.filter(product=product)
    costs_data = list(costs.values('year', 'base_cost', 'labor_cost', 'material_cost', 'overhead_cost'))
    return render(request, 'core/product/product_read.html', {
        'product_data': product_data,
        'volume_data': volume_data,
        'prices_data': prices_data,
        'costs_data': costs_data,
    })


@csrf_exempt
def save_product_changes(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            updated_data = data.get('updated_data', [])

            with transaction.atomic():
                for item in updated_data:
                    try:
                        volume_data = Volume.objects.get(id=item['id'])
                        volume_data.year = item['year']
                        volume_data.min_volume = item['min_volume']
                        volume_data.expected_volume = item['expected_volume']
                        volume_data.max_volume = item['max_volume']
                        volume_data.save()
                        print(f"Updating volume with ID {item['id']}")
                        print(f"New values: {item['year']}, {item['min_volume']}, {item['expected_volume']}, {item['max_volume']}")


                    except Volume.DoesNotExist:
                        # Log the ID of the missing volume for debugging purposes
                        print(f"Volume with ID {item['id']} not found")

            return JsonResponse({'success': True})

        except Exception as e:
            # Log the full exception for debugging purposes
            print(f"Error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def create_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm()

    return render(request, 'core/product/product_create.html', {'form': form})

@login_required
def show_projects(request):
    projects = Project.objects.all(); 
    return render(request, 'core/project/project_read.html', {'projects': projects})

@login_required
def create_or_edit_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.responsible = request.user
            project.save()
            return redirect('project_list')  

    else:
        form = ProjectForm()

    return render(request, 'core/project/project_create.html', {'form': form})

@login_required
def view_project(request, id):
    project = get_object_or_404(Project, id=id)
    return render(request, 'core/project/project_read.html', {'project': project})

@login_required
def delete_project(request, id):
    project = get_object_or_404(Project, id=id)
    return render(request, 'core/project/project_delete.html', {'project': project})

    