from django.urls import path
from .views import index, delete_user ,change_password, edit_user, RegisterPage, UserListView, SalesListView, generate_pdf, ProductDetailView, CreateProduct, UpdateProduct, TaskDelete, CustomLoginView, logout_view, CreateSaleView, DashboardView, assign_group

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('sales/', CreateSaleView.as_view(), name='sales'),
    path('view-sales/', SalesListView.as_view(), name='view-sales'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),
    path('user/', UserListView.as_view(), name='user'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='products'),
    path('add-product/', CreateProduct.as_view(), name='add-product'),
    path('update-product/<int:pk>/', UpdateProduct.as_view(), name='update-product'),
    path('delete-product/<int:pk>/', TaskDelete.as_view(), name='delete-product'),
    path('generate-pdf/', generate_pdf, name='generate_pdf'),
    path('assign-group/<int:user_id>/', assign_group, name='assign_group'),
    path('delete-user/<int:pk>/', delete_user, name='delete_user'),
    path('edit-user/<int:pk>/', edit_user, name='edit_user'),
    path('change-password/<int:pk>/', change_password, name='change_password'),
    path('index/', index, name='index'),
]