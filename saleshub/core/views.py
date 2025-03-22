from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required 
from .models import Product, Pricing, Volume, Cost, Project, Item
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.exceptions import ObjectDoesNotExist
from .forms import ProductForm, ProjectForm, ItemForm
import logging

logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------STRUCTURE--------------------------------------------------------------------------------

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

#-------------------------------------------------------------------PRODUCTS----------------------------------------------------------------------------------------

@login_required
def show_products(request):
    products = Product.objects.all()
    return render(request, 'core/product/product_list.html', {'products': products})

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

@login_required
def create_or_edit_product(request, id=None):

    if id:
        product = get_object_or_404(Product, id=id)
    else:
        product = None

    if request.method == "POST":
        form = ProductForm(request.POST, instance = product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'core/product/product_create_or_edit.html', {'form': form})

@login_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.delete()
        return redirect('product_list')

    return render(request, 'core/product/product_delete.html', {'product': product})

#----------------------------------------------------------------------------PROJECTS-----------------------------------------------------------------------------

@login_required
def show_projects(request):
    projects = Project.objects.all(); 
    return render(request, 'core/project/project_list.html', {'projects': projects})

@login_required
def create_or_edit_project(request, id=None):
    if id:
        project = get_object_or_404(Project, id=id)
    else:
        project = None

    if request.method == "POST":
        form = ProjectForm(request.POST, instance = project)
        if form.is_valid():
            project = form.save(commit=False)
            project.responsible = request.user
            project.save()
            return redirect('project_list')  

    else:
        form = ProjectForm(instance=project)

    return render(request, 'core/project/project_create_or_edit.html', {'form': form, 'object' : project})

@login_required
def view_project(request, id):
    project = get_object_or_404(Project, id=id)
    return render(request, 'core/project/project_read.html', {'project': project})

@login_required
def delete_project(request, id):
    project = get_object_or_404(Project, id=id)

    if request.method == "POST":
        project.delete()
        return redirect('project_list')

    return render(request, 'core/project/project_delete.html', {'project': project})

def add_item_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.project = project
            item.save()

            current_year = 2025
            schedule_years = form.cleaned_data.get('schedule_years', 5)

            for i in range(schedule_years):
                year = current_year + i

                Volume.objects.create(
                    item=item,
                    year=year,
                    min_volume=None,
                    expected_volume=None,
                    max_volume=None
                )

                Pricing.objects.create(
                    item=item,
                    year=year,
                    base_price=None,
                    packaging_price=None,
                    transport_price=None,
                    warehouse_price=None
                )

                Cost.objects.create(
                    item=item,
                    year=year,
                    base_cost=None,
                    labor_cost=None,
                    material_cost=None,
                    overhead_cost=None
                )

            return redirect('project_read', id=project.id)
    else:
        form = ItemForm()

    return render(request, 'core/item/item_create.html', {'form': form, 'project': project})

#------------------------------------------------------------ITEM---------------------------------------------------------------------------------------------------

def item_read_or_update(request, project_id, item_id):
    item = get_object_or_404(Item, id=item_id, project_id=project_id)

    volume = Volume.objects.filter(item=item)
    pricings = Pricing.objects.filter(item=item)
    costing = Cost.objects.filter(item=item)

    context = {
    'item': item,
    'volume': list(volume.values()) if volume else [],
    'pricings': list(pricings.values()) if pricings else [],
    'costing': list(costing.values()) if costing else [],
    }

    return render(request, 'core/item/item_read_or_update.html', context)

def get_volume_data(request, item_id):
    volume = list(Volume.objects.filter(item__id=item_id).values())
    return JsonResponse({"volume": volume})

def get_pricing_data(request, item_id):
    pricing = list(Pricing.objects.filter(item__id=item_id).values())
    return JsonResponse({"pricing": pricing})

def get_cost_data(request, item_id):
    costing = list(Cost.objects.filter(item__id=item_id).values())
    return JsonResponse({"costing": costing})

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Item, Volume
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def save_volume_data(request, item_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

    try:
        raw_body = request.body.decode('utf-8')
        logger.info(f"Raw request body: {raw_body}")
        print("Received raw body:", raw_body)
        data = json.loads(raw_body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)

    try:
        item = Item.objects.get(id=item_id)
    except ObjectDoesNotExist:
        return JsonResponse({"status": "error", "message": "Item not found."}, status=404)

    if "volume" not in data or not isinstance(data["volume"], list):
        return JsonResponse({"status": "error", "message": "Invalid data format."}, status=400)

    volumes = data["volume"]
    saved_volumes = []

    for volume_data in volumes:
        volume_id = volume_data.get("id")
        year = volume_data.get("year")
        min_volume = volume_data.get("min_volume")
        expected_volume = volume_data.get("expected_volume")
        max_volume = volume_data.get("max_volume")

        try:
            year = int(year)
            min_volume = int(min_volume) if min_volume is not None else None
            expected_volume = int(expected_volume) if expected_volume is not None else None
            max_volume = int(max_volume) if max_volume is not None else None
        except ValueError:
            return JsonResponse({"status": "error", "message": f"Invalid number format for year {year}."}, status=400)

        if volume_id:
            try:
                volume = Volume.objects.get(id=volume_id)
                volume.year = year
                volume.min_volume = min_volume
                volume.expected_volume = expected_volume
                volume.max_volume = max_volume
                volume.save()
            except Volume.DoesNotExist:
                return JsonResponse({"status": "error", "message": f"Volume ID {volume_id} not found."}, status=404)
        else:
            volume = Volume.objects.create(
                item=item,
                year=year,
                min_volume=min_volume,
                expected_volume=expected_volume,
                max_volume=max_volume
            )

        saved_volumes.append({
            "id": volume.id,
            "year": volume.year,
            "min_volume": volume.min_volume,
            "expected_volume": volume.expected_volume,
            "max_volume": volume.max_volume
        })

    return JsonResponse({"status": "success", "volumes": saved_volumes}, status=200)

@csrf_exempt
def save_pricing_data(request, item_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)

        pricing_data = data.get("pricing", [])
        updated_count = 0

        for price in pricing_data:
            updated = Pricing.objects.filter(id=price["id"]).update(
                year=price["year"],
                base_price=price["base_price"],
                packaging_price=price["packaging_price"],
                transport_price=price["transport_price"],
                warehouse_price=price["warehouse_price"],
            )
            updated_count += updated

        return JsonResponse({"status": "success", "updated_count": updated_count})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

@csrf_exempt
def save_costing_data(request, item_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)

        costing_data = data.get("costing", [])  # Corectat "costING" in "costing"
        updated_count = 0

        for cost in costing_data:
            updated = Cost.objects.filter(id=cost["id"]).update(
                year=cost["year"],
                base_cost=cost["base_cost"],
                labor_cost=cost["labor_cost"],
                material_cost=cost["material_cost"],
                overhead_cost=cost["overhead_cost"],
            )
            updated_count += updated

        return JsonResponse({"status": "success", "updated_count": updated_count})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)