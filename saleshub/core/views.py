from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required 
from .models import Product, Pricing, Volume, Cost, Project, Item, Category, Customer, Location, UserRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.exceptions import ObjectDoesNotExist
from .forms import ProductForm, ProjectForm, ItemForm, CategoryRequestForm, LocationRequestForm, CustomerRequestForm, ContractUploadForm
import logging
from django.contrib.admin.views.decorators import staff_member_required
from decimal import Decimal
from collections import defaultdict

logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------STRUCTURE--------------------------------------------------------------------------------

@login_required
def home(request):
    products = Product.objects.all()

    status_values = ['approved', 'pending', 'rejected']
    revenue_by_status = {}

    for status in status_values:
        projects = Project.objects.filter(acquisition_status=status)
        total_revenue = 0

        for project in projects:
            for item in project.items.all():
                volumes = item.volume.all()
                pricing = item.pricing.all()

                for v in volumes:
                    price_obj = pricing.filter(year=v.year).first()
                    if v.expected_volume and price_obj and price_obj.base_price:
                        total_revenue += float(v.expected_volume) * float(price_obj.base_price)

        revenue_by_status[status.capitalize()] = round(total_revenue, 2)

    labels = list(revenue_by_status.keys())
    values = list(revenue_by_status.values())

    return render(request, 'core/structure/home.html', {
        'products': products,
        'labels': labels,
        'values': values
    })

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

#-------------------------------------------------------------------PRODUCT----------------------------------------------------------------------------------------

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

#----------------------------------------------------------------------------PROJECT-----------------------------------------------------------------------------

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

    # Upload contract
    if request.method == "POST" and 'upload_contract' in request.POST:
        contract_form = ContractUploadForm(request.POST, request.FILES)
        if contract_form.is_valid():
            contract = contract_form.save(commit=False)
            contract.project = project
            contract.save()
            return redirect('project_read', id=project.id)

    # Update proiect
    elif request.method == "POST":
        project.dos = request.POST.get('dos')
        project.sop = request.POST.get('sop')
        project.eop = request.POST.get('eop')
        project.acquisition_status = request.POST.get('acquisition_status')
        project.acquisition_probability = request.POST.get('acquisition_probability')
        project.save()
        return redirect('project_read', pk=project.id)

    # Form de upload gol pentru template
    contract_form = ContractUploadForm()

    return render(request, 'core/project/project_read.html', {
        'project': project,
        'form': contract_form
    })

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

@csrf_exempt
def save_volume_data(request, item_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

    try:
        raw_body = request.body.decode('utf-8')
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

        costing_data = data.get("costing", [])
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
    
from django.shortcuts import get_object_or_404, redirect, render
from core.models import Item

@login_required
def item_delete_view(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        project_id = item.project.id
        item.delete()
        return redirect('project_read', project_id)

    return render(request, 'core/item/item_delete.html', {
        'item': item
    })

    
#----------------------------------------------------------REQUEST--------------------------------------------------------------------------------------------------

@login_required
def send_request_view(request):
    if request.method == "POST":
        req_type = request.POST.get("request_type")
        form = None

        if req_type == "category":
            form = CategoryRequestForm(request.POST)
        elif req_type == "customer":
            form = CustomerRequestForm(request.POST)
        elif req_type == "location":
            form = LocationRequestForm(request.POST)

        if form and form.is_valid():
            UserRequest.objects.create(
                request_type=req_type,
                data=form.cleaned_data,  # ✅ aici e cheia
                created_by=request.user,
            )
            return redirect('send_request')

    return render(request, 'core/request/request_create.html', {
        'category_form': CategoryRequestForm(),
        'customer_form': CustomerRequestForm(),
        'location_form': LocationRequestForm(),
    })


@staff_member_required
def manage_requests_view(request):
    requests = UserRequest.objects.filter(is_approved=False).order_by('-created_at')

    categories = Category.objects.all()
    customers = Customer.objects.all()
    locations = Location.objects.all()

    if request.method == "POST":
        if "approve" in request.POST:
            req = get_object_or_404(UserRequest, id=request.POST.get("req_id"))
            data = req.data

            if req.request_type == 'category':
                Category.objects.create(name=data['name'])
            elif req.request_type == 'customer':
                Customer.objects.create(name=data['name'], email=data['email'])
            elif req.request_type == 'location':
                Location.objects.create(address=data['address'], city=data['city'], country=data['country'])

            req.is_approved = True
            req.save()

        elif "reject" in request.POST:
            req = get_object_or_404(UserRequest, id=request.POST.get("req_id"))
            req.delete()

        elif "delete_category_id" in request.POST:
            Category.objects.filter(id=request.POST.get("delete_category_id")).delete()
        elif "delete_customer_id" in request.POST:
            Customer.objects.filter(id=request.POST.get("delete_customer_id")).delete()
        elif "delete_location_id" in request.POST:
            Location.objects.filter(id=request.POST.get("delete_location_id")).delete()

        return redirect('manage_requests')

    return render(request, 'core/request/request_admin.html', {
        'requests': requests,
        'categories': categories,
        'customers': customers,
        'locations': locations
    })

#------------------------------------------------------------------------DASHBOARD-------------------------------------------------------------------------

def dashboard_view(request):

    years = list(range(2025, 2033))
    cat_labels, cat_values = get_revenue_by_category()
    loc_labels, loc_values = get_revenue_by_location()
    cus_labels, cus_values = get_revenue_by_customer()
    prod_labels, prod_values = get_revenue_by_product()
    years, revenue_vals, cost_vals, ebit_vals = get_revenue_and_cost_by_year()
    vol_min, vol_exp, vol_max = get_volume_projection()

    return render(request, 'core/dashboard/dashboards.html', {
        'category_labels': cat_labels,
        'category_values': cat_values,
        'location_labels': loc_labels,
        'location_values': loc_values,
        'customer_labels': cus_labels,
        'customer_values': cus_values,
        'product_labels': prod_labels,
        'product_values': prod_values,
        'years_range': years,
        'revenue_values': revenue_vals,
        'cost_values': cost_vals,
        'ebit_values': ebit_vals,
        'volume_min': vol_min,
        'volume_exp': vol_exp,
        'volume_max': vol_max
    })


def get_revenue_by_category():
    category_labels = []
    category_values = []

    for category in Category.objects.all():
        total_revenue = Decimal(0)
        products = category.product_set.all()

        items = Item.objects.filter(product__in=products)

        for item in items:
            volumes = item.volume.all()
            pricing = item.pricing.all()

            for volume in volumes:
                price = pricing.filter(year=volume.year).first()
                if volume.expected_volume and price:
                    final_price = sum(filter(None, [
                        price.base_price,
                        price.packaging_price,
                        price.transport_price,
                        price.warehouse_price
                    ]))
                    revenue = Decimal(volume.expected_volume) * final_price
                    total_revenue += revenue

        category_labels.append(category.name)
        category_values.append(float(total_revenue))

    return category_labels, category_values

def get_revenue_by_location():
    location_labels = []
    location_values = []

    for location in Location.objects.all():
        total_revenue = Decimal(0)
        items = Item.objects.filter(location=location)

        for item in items:
            volumes = item.volume.all()
            pricing = item.pricing.all()

            for volume in volumes:
                price = pricing.filter(year=volume.year).first()
                if volume.expected_volume and price:
                    final_price = sum(filter(None, [
                        price.base_price,
                        price.packaging_price,
                        price.transport_price,
                        price.warehouse_price
                    ]))
                    total_revenue += Decimal(volume.expected_volume) * final_price

        location_labels.append(str(location))
        location_values.append(float(total_revenue))

    return location_labels, location_values

def get_revenue_by_customer():
    customer_labels = []
    customer_values = []

    for customer in Customer.objects.all():
        total_revenue = Decimal(0)
        items = Item.objects.filter(project__customer=customer)

        for item in items:
            volumes = item.volume.all()
            pricing = item.pricing.all()

            for volume in volumes:
                price = pricing.filter(year=volume.year).first()
                if volume.expected_volume and price:
                    final_price = sum(filter(None, [
                        price.base_price,
                        price.packaging_price,
                        price.transport_price,
                        price.warehouse_price
                    ]))
                    total_revenue += Decimal(volume.expected_volume) * final_price

        customer_labels.append(customer.name)
        customer_values.append(float(total_revenue))

    return customer_labels, customer_values

def get_revenue_by_product():
    product_labels = []
    product_values = []

    for product in Product.objects.all():
        total_revenue = Decimal(0)
        items = Item.objects.filter(product=product)

        for item in items:
            volumes = item.volume.all()
            pricing = item.pricing.all()

            for volume in volumes:
                price = pricing.filter(year=volume.year).first()
                if volume.expected_volume and price:
                    final_price = sum(filter(None, [
                        price.base_price,
                        price.packaging_price,
                        price.transport_price,
                        price.warehouse_price
                    ]))
                    total_revenue += Decimal(volume.expected_volume) * final_price

        product_labels.append(product.name)
        product_values.append(float(total_revenue))

    return product_labels, product_values

def get_revenue_and_cost_by_year():
    years_range = list(range(2025, 2033))
    revenue_by_year = defaultdict(Decimal)
    cost_by_year = defaultdict(Decimal)
    ebit_by_year = defaultdict(Decimal)

    for item in Item.objects.all():
        volumes = item.volume.all()
        pricing = item.pricing.all()
        costing = item.costing.all()

        for volume in volumes:
            if volume.year not in years_range:
                continue

            price = pricing.filter(year=volume.year).first()
            cost = costing.filter(year=volume.year).first()

            if volume.expected_volume and price:
                final_price = sum(filter(None, [
                    price.base_price,
                    price.packaging_price,
                    price.transport_price,
                    price.warehouse_price
                ]))
                revenue = Decimal(volume.expected_volume) * final_price
                revenue_by_year[volume.year] += revenue

            if volume.expected_volume and cost:
                total_cost = sum(filter(None, [
                    cost.base_cost,
                    cost.labor_cost,
                    cost.material_cost,
                    cost.overhead_cost
                ]))
                cost_total = Decimal(volume.expected_volume) * total_cost
                cost_by_year[volume.year] += cost_total

    for y in years_range:
        ebit_by_year[y] = revenue_by_year[y] - cost_by_year[y]

    return (
    years_range,
    [float(revenue_by_year[y]) for y in years_range],
    [float(cost_by_year[y]) for y in years_range],
    [float(ebit_by_year[y]) for y in years_range]
)


def get_volume_projection():

    years_range = list(range(2025, 2033))
    volume_min_by_year = defaultdict(Decimal)
    volume_exp_by_year = defaultdict(Decimal)
    volume_max_by_year = defaultdict(Decimal)

    for item in Item.objects.all():
        for volume in item.volume.all():
            if volume.year not in years_range:
                continue

            if volume.min_volume:
                volume_min_by_year[volume.year] += Decimal(str(volume.min_volume))
            if volume.expected_volume:
                volume_exp_by_year[volume.year] += Decimal(str(volume.expected_volume))
            if volume.max_volume:
                volume_max_by_year[volume.year] += Decimal(str(volume.max_volume))

    return ([float(volume_min_by_year[y]) for y in years_range],
    [float(volume_exp_by_year[y]) for y in years_range],
    [float(volume_max_by_year[y]) for y in years_range])








