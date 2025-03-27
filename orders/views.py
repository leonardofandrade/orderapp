from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, F
from django.forms import inlineformset_factory
from .models import Order, Product, ProductCategory, OrderItem
from .forms import OrderForm, OrderItemForm

def get_product_price(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return JsonResponse({'price': str(product.price)})

def create_order(request):
    order_id = request.GET.get('order_id')
    if order_id:
        order = get_object_or_404(Order, id=order_id)
        if request.method == 'POST':
            form = OrderForm(request.POST, instance=order)
            formset = OrderItemFormSet(request.POST, instance=order)
            if form.is_valid() and formset.is_valid():
                order = form.save()
                instances = formset.save(commit=False)
                for obj in formset.deleted_objects:
                    obj.delete()
                for instance in instances:
                    instance.order = order
                    if not instance.item_price and instance.product:
                        instance.item_price = instance.product.price
                    instance.save()
                formset.save_m2m()
                order.calculate_total()
                messages.success(request, 'Order updated successfully!')
                return redirect('order_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = OrderForm(instance=order)
            formset = OrderItemFormSet(instance=order)
    else:
        if request.method == 'POST':
            form = OrderForm(request.POST)
            formset = OrderItemFormSet(request.POST)
            if form.is_valid() and formset.is_valid():
                order = form.save()
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.order = order
                    if not instance.item_price and instance.product:
                        instance.item_price = instance.product.price
                    instance.save()
                order.calculate_total()
                messages.success(request, 'Order created successfully!')
                return redirect('order_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = OrderForm()
            formset = OrderItemFormSet()
    
    products = Product.objects.all().select_related('category')
    return render(request, 'orders/order_form_final.html', {
        'form': form,
        'formset': formset,
        'products': products,
        'is_edit': bool(order_id)
    })

def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

# Category Views
def category_list(request):
    categories = ProductCategory.objects.all()
    return render(request, 'orders/category_list.html', {'categories': categories})

def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            ProductCategory.objects.create(name=name, description=description)
            messages.success(request, 'Category created successfully!')
        else:
            messages.error(request, 'Category name is required.')
        return redirect('category_list')
    return redirect('category_list')

def edit_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(ProductCategory, id=category_id)
        name = request.POST.get('name')
        if name:
            category.name = name
            category.description = request.POST.get('description')
            category.save()
            messages.success(request, 'Category updated successfully!')
        else:
            messages.error(request, 'Category name is required.')
    return redirect('category_list')

def delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(ProductCategory, id=category_id)
        try:
            category.delete()
            messages.success(request, 'Category deleted successfully!')
        except Exception as e:
            messages.error(request, 'Cannot delete category. It may have associated products.')
    return redirect('category_list')

# Product Views
def product_list(request):
    products = Product.objects.all().select_related('category')
    categories = ProductCategory.objects.all()
    return render(request, 'orders/product_list.html', {
        'products': products,
        'categories': categories
    })

def create_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        
        if name and price and category_id:
            try:
                category = get_object_or_404(ProductCategory, id=category_id)
                Product.objects.create(
                    name=name,
                    price=price,
                    category=category
                )
                messages.success(request, 'Product created successfully!')
            except Exception as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'All fields are required.')
        return redirect('product_list')
    return redirect('product_list')

def edit_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        name = request.POST.get('name')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        
        if name and price and category_id:
            try:
                category = get_object_or_404(ProductCategory, id=category_id)
                product.name = name
                product.price = price
                product.category = category
                product.save()
                messages.success(request, 'Product updated successfully!')
            except Exception as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'All fields are required.')
    return redirect('product_list')

def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        try:
            product.delete()
            messages.success(request, 'Product deleted successfully!')
        except Exception as e:
            messages.error(request, 'Cannot delete product. It may be used in orders.')
    return redirect('product_list')

def delete_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        try:
            order.delete()
            messages.success(request, 'Order deleted successfully!')
        except Exception as e:
            messages.error(request, str(e))
    return redirect('order_list')

# Create OrderItemFormSet
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    fields=('product', 'quantity', 'item_price'),
    extra=1,
    can_delete=True,
)