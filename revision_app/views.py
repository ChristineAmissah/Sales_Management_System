from django.shortcuts import render, redirect, get_object_or_404
import logging
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.views import LoginView
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.urls import reverse_lazy
from django.http import HttpResponse
from .models import Products,  Sale
from django.contrib.auth import logout
from django.db.models import Sum, F, Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from .forms import SalesForm
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from django.contrib.auth.hashers import make_password
from .forms import ChangePasswordForm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.db import transaction
from .decorators import unauthenicated_user, allowed_users, admin_only
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from .forms import UserEditForm  # Import the form

# Create your views here.


@method_decorator(admin_only, name='dispatch')
class RegisterPage(FormView):
    template_name = 'revision_app/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        """If the form is valid, save the new user and redirect to the dashboard."""
        user = form.save()  # Create the new user
        return super().form_valid(form)  # Redirect after successful creation

    def get_success_url(self):
        """Ensure admins are always redirected to the dashboard after registration."""
        return reverse_lazy('dashboard')


@method_decorator(unauthenicated_user, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'revision_app/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        groups = self.request.user.groups.all()
        if groups[0].name == "admin":
            return reverse_lazy('dashboard')
        else:
            return reverse_lazy('sales')
    
def logout_view(request):
    logout(request)
    return redirect('login')


@method_decorator(admin_only, name='dispatch')
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'revision_app/admin.html'  # Template where products and sales will be displayed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Base querysets
        products = Products.objects.all()
        sales = Sale.objects.all()
        users = User.objects.all()
        user_groups = {}
        
        # Basic statistics
        context['total_products'] = products.exclude(stock=0).count()
        context['total_stock'] = products.aggregate(Sum('stock'))['stock__sum'] or 0
        context['total_value'] = products.aggregate(total=Sum(F('price') * F('stock')))['total'] or 0
        context['total_sales'] = Sale.objects.aggregate(total=Sum(F('quantity_sold') * F('product__price')))['total']or 0  
        
        for user in users:
            user_groups[user.id] = {
                'is_admin': user.groups.filter(name='admin').exists(),
                'is_sales': user.groups.filter(name='sales_person').exists(),
            }

        # Get search input
        search_input = self.request.GET.get('q', '').strip()
        
        if search_input:
            # Try parsing the date with multiple formats
            search_date = None
            date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y']
            
            for date_format in date_formats:
                try:
                    search_date = datetime.strptime(search_input, date_format).date()
                    break
                except ValueError:
                    continue
            
            if search_date:
                # Filter sales by date using a date range to capture all entries for that day
                sales = sales.filter(
                    date_sold__date=search_date
                )
            else:
                # If not a date, filter by other fields
                products = products.filter(
                    Q(product_name__icontains=search_input) |
                    Q(stock__icontains=search_input) |
                    Q(price__icontains=search_input) |
                    Q(unique_key__icontains=search_input)
                )
                
                sales = sales.filter(
                    Q(product__product_name__icontains=search_input) |
                    Q(salesperson__username__icontains=search_input) |
                    Q(unique_key__icontains=search_input) |
                    Q(total_price__icontains=search_input) |
                    Q(quantity_sold__icontains=search_input)
                )
        
        # Update context with filtered querysets
        context['products'] = products
        context['sales'] = sales
        context['search_input'] = search_input
        context['users'] = users
        
        return context

class SalesListView(LoginRequiredMixin, TemplateView):
    template_name = 'revision_app/sales.html'  # Template where products and sales will be displayed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sales = Sale.objects.all()
        products = Products.objects.all()

        search_input = self.request.GET.get('q', '').strip()
        
        if search_input:
            # Try parsing the date with multiple formats
            search_date = None
            date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y']
            
            for date_format in date_formats:
                try:
                    search_date = datetime.strptime(search_input, date_format).date()
                    break
                except ValueError:
                    continue
            
            if search_date:
                # Filter sales by date using a date range to capture all entries for that day
                sales = sales.filter(
                    date_sold__date=search_date
                )
            else:
                # If not a date, filter by other fields
                products = products.filter(
                    Q(product_name__icontains=search_input) |
                    Q(stock__icontains=search_input) |
                    Q(price__icontains=search_input) |
                    Q(unique_key__icontains=search_input)
                )
                
                sales = sales.filter(
                    Q(product__product_name__icontains=search_input) |
                    Q(salesperson__username__icontains=search_input) |
                    Q(unique_key__icontains=search_input) |
                    Q(total_price__icontains=search_input) |
                    Q(quantity_sold__icontains=search_input)
                )

        context['products'] = products
        context['sales'] = sales
        return context
        
class UserListView(LoginRequiredMixin, TemplateView):
    template_name = 'revision_app/user.html'  # Template where products and sales will be displayed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.all()
        user_groups = {}

        for user in users:
            user_groups[user.id] = {
                'is_admin': user.groups.filter(name='admin').exists(),
                'is_sales': user.groups.filter(name='sales_person').exists(),
            }

        # Get search input
        search_input = self.request.GET.get('q', '').strip()
        
        if search_input:
            users = users.filter(
                    Q(username__icontains=search_input) |
                    Q(email__icontains=search_input) |
                    Q(first_name__icontains=search_input) |
                    Q(last_name__icontains=search_input)
                )
        
        # Update context with filtered querysets

        context['search_input'] = search_input

        context['users'] = users
        return context


@allowed_users(allowed_roles=['admin'])
@require_POST    
def assign_group(request, user_id):
    user = User.objects.get(pk=user_id)
    selected_group = request.POST.get('group')

    # Remove the user from any existing group (if desired)
    user.groups.clear()

    # Assign the user to the selected group
    group = Group.objects.get(name=selected_group)
    user.groups.add(group)

    return redirect('user')

@allowed_users(allowed_roles=['admin'])
def change_password(request, pk):
    user = get_object_or_404(User, id=pk)

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.password = make_password(new_password)  # Hash the new password
            user.save()
            return redirect('user') 
    else:
        form = ChangePasswordForm()

    return render(request, 'revision_app/change_password.html', {'form': form, 'user': user})

@allowed_users(allowed_roles=['admin'])
# Edit user view
def edit_user(request, pk):  # Change 'user_id' to 'pk'
    user = get_object_or_404(User, id=pk)  # Use 'pk' to fetch the user
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user')  # Redirect to the dashboard or any page of your choice
    else:
        form = UserEditForm(instance=user)
    return render(request, 'revision_app/edit_user.html', {'form': form, 'user': user})


@allowed_users(allowed_roles=['admin'])
# Delete user view
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('user')  # Redirect to your dashboard

    return render(request, 'revision_app/admin.html')



# dispay details of what is happening
@method_decorator(allowed_users(allowed_roles=['admin']), name='dispatch')
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Products
    context_object_name = 'products'
    template_name = 'revision_app/product_detail.html'
    
    def form_valid(self, form):
        # You can add custom logic here before saving the form
        print("Form is valid. Saving the product...")
        return super().form_valid(form)
    
# add stuff to the table
@method_decorator(allowed_users(allowed_roles=['admin']), name='dispatch')
class CreateProduct(LoginRequiredMixin, CreateView):
    model = Products
    fields = '__all__' #list all the items to the view
    success_url = reverse_lazy('dashboard')
    # template_name = 'base/add_products.html'

# so basically, when you have to name the template, it is template/no of app/ your files
@method_decorator(allowed_users(allowed_roles=['admin']), name='dispatch')
class UpdateProduct(LoginRequiredMixin, UpdateView):
    model = Products
    fields = '__all__'
    success_url = reverse_lazy('dashboard')

@method_decorator(allowed_users(allowed_roles=['admin']), name='dispatch')
class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Products
    context_object_name = 'products'
    success_url = reverse_lazy('dashboard')

# sales view
class CreateSaleView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SalesForm
    context_object_name = 'sales'
    template_name = 'revision_app/sales_form.html'
    success_url = reverse_lazy('sales')  # Redirect to sales page after success

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sales'] = Sale.objects.all()  # Retrieve all sales records
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Get the product and quantity
                product = form.cleaned_data['product']
                quantity = form.cleaned_data['quantity_sold']
                
                # Check if enough stock is available
                if product.stock < quantity:
                    messages.error(self.request, f'Not enough stock! Only {product.stock} available.')
                    return self.form_invalid(form)
                
                # Calculate total price
                total_price = product.price * quantity
                
                # Create the sale
                sale = form.save(commit=False)
                sale.salesperson = self.request.user
                sale.total_price = total_price
                sale.date_sold = timezone.now()
                sale.save()  # Save the sale to the database
                
                # Update product stock
                product.stock -= quantity
                product.save()  # Save the updated product stock
                
                messages.success(self.request, f'Successfully sold {quantity} {product.product_name}.')
                return super().form_valid(form)
            logger = logging.getLogger(__name__)
            
        except Exception as e:
            logger.error(f'Error processing sale: {str(e)}')
            messages.error(self.request, f'Error processing sale: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error processing sale. Please check your inputs.')
        return super().form_invalid(form)


# Generate PDF Report
@allowed_users(allowed_roles=['admin'])
def generate_pdf(request):
    # Create a HttpResponse object with the appropriate PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Create a SimpleDocTemplate for easier layout management
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Define the table data, including headers
    sales_data = Sale.objects.all().select_related('salesperson').values(
        'product__product_name',
        'quantity_sold',
        'total_price',
        'date_sold',
        'salesperson__username'  # Access the username of the salesperson
    )

    table_data = [['Product', 'Quantity Sold', 'Total Price (Cedis)', 'Date Sold | Time Sold', 'Sales Person']]  # Table headers

    # Populate the table with sales data
    for sale in sales_data:
        table_data.append([
            sale['product__product_name'],
            sale['quantity_sold'],
            f"{sale['total_price']:.2f}",  # Format the total price with 2 decimals
            sale['date_sold'].strftime("%Y-%m-%d %H:%M") if sale['date_sold'] else 'N/A',  # Format the date
            sale['salesperson__username'] if sale['salesperson__username'] else 'N/A'  # Access the username
        ])

    # Create the Table object
    table = Table(table_data)

    # Add some table styling
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Header row background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center-align text horizontally
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Center-align text vertically
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for headers
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Background for data rows
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grid for the table
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),  # Ensure all data cells are center-aligned
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),  # Header font bold
    ]))

    # Build the document
    doc.build([table])

    return response

