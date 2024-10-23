from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from django.http import HttpResponse
from .models import Products,  Sale
from django.contrib.auth import logout
from django.db.models import Sum, F, Q
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from .forms import SalesForm
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.db import transaction
# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'revision_app/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')
    
def logout_view(request):
    logout(request)
    return redirect('login')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'revision_app/admin.html'  # Template where products and sales will be displayed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Products.objects.all()  # Fetch all products
        context['sales'] = Sale.objects.all()  # Fetch all sales
        context['total_products'] = Products.objects.exclude(stock=0).count()
        context['total_stock'] = Products.objects.aggregate(Sum('stock'))['stock__sum'] or 0
        context['total_value'] = Products.objects.aggregate(total=Sum(F('price') * F('stock')))['total'] or 0 
        context['total_sales'] = Sale.objects.aggregate(total=Sum(F('quantity_sold') * F('total_price')))['total']or 0  
        # Get the price from the Products model).aggregate(total=Sum(F('quantity_sold') * F('product_price')))['total'] or 0
        search_input =  self.request.GET.get('q') or ''
        products = Products.objects.all()
        sales = Sale.objects.all()
        if search_input:
            products = products.filter(product_name__icontains=search_input)
            sales = sales.filter(product__product_name__icontains=search_input)
        
        context['products'] = products
        context['sales'] = sales
        context['search_input'] = search_input
        return context


#         # Search in Sales
#          | Q(quantity_sold__icontains=query))

#     context = {
#         'products': products,
#         'sales': sales,
#         'query': query,
#     }
    
#     return render(request, 'revision_app/admin.html', context)
    

# dispay details of what is happening
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Products
    context_object_name = 'products'
    template_name = 'revision_app/product_detail.html'
    
    def form_valid(self, form):
        # You can add custom logic here before saving the form
        print("Form is valid. Saving the product...")
        return super().form_valid(form)
    
# add stuff to the table
class CreateProduct(LoginRequiredMixin, CreateView):
    model = Products
    fields = '__all__' #list all the items to the view
    success_url = reverse_lazy('dashboard')
    # template_name = 'base/add_products.html'

# so basically, when you have to name the template, it is template/no of app/ your files
class UpdateProduct(LoginRequiredMixin, UpdateView):
    model = Products
    fields = '__all__'
    success_url = reverse_lazy('dashboard')

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
        # Get the product and quantity from the form data
        product = form.cleaned_data['product']  # Ensure this references the Product instance
        quantity_sold = form.cleaned_data['quantity_sold']

        # Check if the requested quantity is available
        if product.stock >= quantity_sold:
            with transaction.atomic():  # Ensure atomic operation for safety
                # Decrease stock by the quantity sold
                product.stock -= quantity_sold
                product.save()  # Save the updated product data

                # Create the sales record but don't save it yet
                sale = form.save(commit=False)
                sale.total_price = product.price * quantity_sold  # Set the total price for the sale
                sale.save()  # Save the sales record to the database

            # Success message
            messages.success(self.request, f'Successfully sold {quantity_sold} {product.product_name}{"" if quantity_sold == 1 else "s"}.')
            return super().form_valid(form)
        else:
            # If the quantity is not available, show an error message
            messages.error(self.request, f'Only {product.stock} of {product.product_name} is available.')
            return self.form_invalid(form)


# Generate PDF Report
def generate_pdf(request):
    # Create a HttpResponse object with the appropriate PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Create a SimpleDocTemplate for easier layout management
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Define the table data, including headers
    sales_data = Sale.objects.all().values('product__product_name', 'quantity_sold', 'total_price', 'date_sold')
    
    table_data = [['Product', 'Quantity Sold', 'Total Price(cedis)', 'Date Sold | Time sold']]  # Table headers

    # Populate the table with sales data
    for sale in sales_data:
        table_data.append([
            sale['product__product_name'], 
            sale['quantity_sold'], 
            f"{sale['total_price']:.2f}",  # Format the total price with 2 decimals
            sale['date_sold'].strftime("%Y-%m-%d  %H:%M")  # Format the date
        ])

    col_widths = [2 * inch, 1.5 * inch, 1.5 * inch, 2.5 * inch]
    # Create the Table object
    table = Table(table_data, colWidths=col_widths)

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

