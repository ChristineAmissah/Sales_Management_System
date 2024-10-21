from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponse
from .models import Products
from django.contrib.auth import logout
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'revision_app/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('product')
    
def logout_view(request):
    logout(request)
    return redirect('login')
    
# used to display a list of objects
class ProductListView(LoginRequiredMixin, ListView):
    model = Products
    # object name change
    context_object_name = 'products'
    template_name = 'revision_app/admin.html'
    paginate_by = 15

    def get_queryset(self):
        # Get all products by default
        queryset = super().get_queryset()
        search_input = self.request.GET.get('search', '')

        # Filter based on search input
        if search_input:
            queryset = queryset.filter(product_name__icontains=search_input)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_input'] = self.request.GET.get('search', '')

        context['total_products'] = Products.objects.count()
        context['total_stock'] = Products.objects.aggregate(Sum('stock'))['stock__sum'] or 0
        context['total_value'] = Products.objects.aggregate(Sum('price'))['price__sum'] or 0
        return context
    

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
    success_url = reverse_lazy('product')
    # template_name = 'base/add_products.html'

# so basically, when you have to name the template, it is template/no of app/ your files
class UpdateProduct(LoginRequiredMixin, UpdateView):
    model = Products
    fields = '__all__'
    success_url = reverse_lazy('product')

class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Products
    context_object_name = 'products'
    success_url = reverse_lazy('product')


def listing(request):
    product_list = Products.objects.all()
    paginator = Paginator(product_list, 25)  # Show 25 contacts per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "admin.html", {"page_obj": page_obj})