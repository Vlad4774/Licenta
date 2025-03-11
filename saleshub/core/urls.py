from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_started, name='get_started'),
    path('home/', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('product/', views.show_products, name='product'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('product/save_changes/', views.save_product_changes, name='product_save_changes'),
    path('product/create', views.create_product, name='create_product'),
    path('project/', views.show_projects, name='project_list'),
    path('project/<int:id>', views.view_project, name='project_read'),
    path('project/<int:id>/edit/', views.show_projects, name='project_update'),
    path('project/<int:id>/delete/', views.delete_project, name='project_delete'),
    path('project/new/', views.create_or_edit_project, name='project_create_or_edit'),
]