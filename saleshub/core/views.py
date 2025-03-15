from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required 
from .models import Product, Pricing, Volume, Cost, Project, Item
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from .forms import ProductForm, ProjectForm, ItemForm

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


def item_read_or_update(request, project_id, item_id):
    item = get_object_or_404(Item, id=item_id, project_id=project_id)

    volumes = Volume.objects.filter(item=item)
    pricings = Pricing.objects.filter(item=item)
    costs = Cost.objects.filter(item=item)

    context = {
    'item': item,
    'volumes': list(volumes.values()) if volumes else [],
    'pricings': list(pricings.values()) if pricings else [],
    'costs': list(costs.values()) if costs else [],
    }

    return render(request, 'core/item/item_read_or_update.html', context)

def get_volume_data(request, item_id):
    volumes = list(Volume.objects.filter(item__id=item_id).values())
    return JsonResponse({"volumes": volumes})

def get_pricing_data(request, item_id):
    pricing = list(Pricing.objects.filter(item__id=item_id).values())
    return JsonResponse({"pricing": pricing})

def get_cost_data(request, item_id):
    costs = list(Cost.objects.filter(item__id=item_id).values())
    return JsonResponse({"costs": costs})

@csrf_exempt
def save_volume_data(request, item_id):
    if request.method == "POST":
        data = json.loads(request.body)
        for volume in data.get("volumes", []):
            Volume.objects.filter(id=volume["id"]).update(
                year=volume["year"],
                min_volume=volume["min_volume"],
                expected_volume=volume["expected_volume"],
                max_volume=volume["max_volume"],
            )
        return JsonResponse({"status": "success"})

@csrf_exempt
def save_pricing_data(request, item_id):
    if request.method == "POST":
        data = json.loads(request.body)
        for price in data.get("pricing", []):
            Pricing.objects.filter(id=price["id"]).update(
                year=price["year"],
                base_price=price["base_price"],
                packaging_price=price["packaging_price"],
                transport_price=price["transport_price"],
                warehouse_price=price["warehouse_price"],
            )
        return JsonResponse({"status": "success"})

@csrf_exempt
def save_cost_data(request, item_id):
    if request.method == "POST":
        data = json.loads(request.body)
        for cost in data.get("costs", []):
            Cost.objects.filter(id=cost["id"]).update(
                year=cost["year"],
                base_cost=cost["base_cost"],
                labor_cost=cost["labor_cost"],
                material_cost=cost["material_cost"],
                overhead_cost=cost["overhead_cost"],
            )
        return JsonResponse({"status": "success"})


@csrf_exempt
def update_item_data(request, item_id):
    """ Actualizează Volume, Pricing și Costing pentru un item """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            item = Item.objects.get(id=item_id)
            product = item.product

            # Actualizăm Volume
            for volume_data in data["volumes"]:
                Volume.objects.update_or_create(id=volume_data.get("id"), defaults=volume_data)

            # Actualizăm Pricing
            for pricing_data in data["pricing"]:
                Pricing.objects.update_or_create(id=pricing_data.get("id"), defaults=pricing_data)

            # Actualizăm Cost
            for cost_data in data["costs"]:
                Cost.objects.update_or_create(id=cost_data.get("id"), defaults=cost_data)

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)



def get_item_data(request, item_id):
    """ Returnează datele de Volume, Pricing și Costing pentru un item """
    try:
        item = Item.objects.get(id=item_id)
        product = item.product

        # Preluăm datele pentru Volume, Pricing și Costing
        volumes = list(Volume.objects.filter(product=product).values("id", "year", "min_volume", "expected_volume", "max_volume"))
        pricing = list(Pricing.objects.filter(product=product).values("id", "year", "base_price", "packaging_price", "transport_price", "warehouse_price"))
        costs = list(Cost.objects.filter(product=product).values("id", "year", "base_cost", "labor_cost", "material_cost", "overhead_cost"))

        return JsonResponse({
            "success": True,
            "volumes": volumes,
            "pricing": pricing,
            "costs": costs
        })

    except Item.DoesNotExist:
        return JsonResponse({"success": False, "error": "Item not found"}, status=404)
    

def save_item_data(request):
    data = json.loads(request.body)
    for item in data.get("volumes", []):
        Volume.objects.filter(id=item["id"]).update(
            min_volume=item["min_volume"],
            expected_volume=item["expected_volume"],
            max_volume=item["max_volume"]
        )
    return JsonResponse({"message": "Saved successfully!"})

    