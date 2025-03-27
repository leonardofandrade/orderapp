from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem, Product

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer email'
            }),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'item_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control select2',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'required': True,
                'placeholder': 'Enter quantity'
            }),
            'item_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'required': True,
                'placeholder': 'Enter price'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.select_related('category')
        
        # Set initial price if we have a product
        if self.instance and hasattr(self.instance, 'product_id') and self.instance.product_id:
            self.fields['item_price'].initial = self.instance.product.price
        
        # Make item_price read-only
        self.fields['item_price'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        
        if product:
            # Set item_price to product price if not set
            if not cleaned_data.get('item_price'):
                cleaned_data['item_price'] = product.price
        
        return cleaned_data

# Create OrderItemFormSet
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    fields=('product', 'quantity', 'item_price'),
    extra=1,
    can_delete=True,
)