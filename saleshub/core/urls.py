from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #structure
    path('', views.get_started, name='get_started'),
    path('home/', views.home, name='home'),
    path('login/', views.user_login, name='login'),

    #product
    path('product/', views.show_products, name='product_list'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('product/<int:id>/delete/', views.delete_product, name='product_delete'),
    path('product/create', views.create_or_edit_product, name='product_create'),
    path('product/<int:id>/edit/', views.create_or_edit_product, name='product_edit'),

    #project
    path('project/', views.show_projects, name='project_list'),
    path('project/<int:id>', views.view_project, name='project_read'),
    path('project/<int:id>/delete/', views.delete_project, name='project_delete'),
    path('project/new/', views.create_or_edit_project, name='project_create'),
    path('project/<int:id>/edit/', views.create_or_edit_project, name='project_edit'),
    path('project/<int:project_id>/add-item/', views.add_item_to_project, name='add_item_to_project'),

    #item
    path('project/<int:project_id>/item/<int:item_id>/', views.item_read_or_update, name='item_read_or_update'),
    path('item/<int:item_id>/delete/', views.item_delete_view, name='item_delete'),
    path('item/<int:item_id>/volume/', views.get_volume_data, name='get_volume_data'),
    path('item/<int:item_id>/pricing/', views.get_pricing_data, name='get_pricing_data'),
    path('item/<int:item_id>/costing/', views.get_cost_data, name='get_cost_data'),
    path('item/<int:item_id>/save-volume/', views.save_volume_data, name='save_volume_data'),
    path('item/<int:item_id>/save-pricing/', views.save_pricing_data, name='save_pricing_data'),
    path('item/<int:item_id>/save-costing/', views.save_costing_data, name='save_costing_data'),

    #request (category, location,  customer)
    path('request/', views.send_request_view, name='send_request'),
    path('pending-request/', views.manage_requests_view, name='manage_requests'),

    #dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/category/', views.dashboard_category_detail, name='dashboard_category_detail'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)