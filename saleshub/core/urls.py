from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_started, name='get_started'),
    path('home/', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('product/', views.show_products, name='product'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('product/create', views.create_product, name='create_product'),
    path('project/', views.show_projects, name='project_list'),
    path('project/<int:id>', views.view_project, name='project_read'),
    path('project/<int:id>/delete/', views.delete_project, name='project_delete'),
    path('project/new/', views.create_or_edit_project, name='project_create'),
    path('project/<int:id>/edit/', views.create_or_edit_project, name='project_edit'),
    path('project/<int:project_id>/add-item/', views.add_item_to_project, name='add_item_to_project'),
    path('item/<int:item_id>/volume/', views.get_volume_data, name='get_volume_data'),
    path('item/<int:item_id>/pricing/', views.get_pricing_data, name='get_pricing_data'),
    path('item/<int:item_id>/costing/', views.get_cost_data, name='get_cost_data'),
    path('project/<int:project_id>/item/<int:item_id>/', views.item_read_or_update, name='item_read_or_update'),
    path('item/<int:item_id>/save-volume/', views.save_volume_data, name='save_volume_data'),
    path('item/<int:item_id>/save-pricing/', views.save_pricing_data, name='save_pricing_data'),
    path('item/<int:item_id>/save-costing/', views.save_costing_data, name='save_cost_data'),
]