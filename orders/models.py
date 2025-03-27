from django.db import models
from django.utils import timezone

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Product Categories"

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, related_name='products', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - ${self.price}"

class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    def calculate_total(self):
        total = sum(item.quantity * item.item_price for item in self.order_items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])
        return total

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if 'update_fields' not in kwargs or 'total_amount' not in kwargs.get('update_fields', []):
            self.calculate_total()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order #{self.order.id}"

    def save(self, *args, **kwargs):
        if not self.item_price and self.product:
            self.item_price = self.product.price
        super().save(*args, **kwargs)
        self.order.calculate_total()
