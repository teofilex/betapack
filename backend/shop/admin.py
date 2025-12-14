from django.contrib import admin
from .models import (
    Category, Subcategory, Product, ProductVariant,
    ProductImage, Order, OrderItem, ContactMessage
)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['name', 'price', 'on_sale', 'sale_price', 'sku', 'in_stock', 'stock_quantity']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['name', 'category__name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'subcategory', 'price', 'on_sale', 'sale_price', 'featured', 'in_stock']
    list_filter = ['category', 'on_sale', 'featured', 'in_stock']
    search_fields = ['name', 'description']
    inlines = [ProductVariantInline, ProductImageInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'price', 'on_sale', 'sale_price', 'current_price', 'in_stock', 'stock_quantity']
    list_filter = ['product__category', 'on_sale', 'in_stock']
    search_fields = ['product__name', 'name', 'sku']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary']
    search_fields = ['product__name', 'alt_text']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'variant_name', 'unit_price', 'total_price']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer_phone', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'customer_email']
    readonly_fields = ['total_amount', 'created_at', 'updated_at', 'sms_sent', 'email_sent']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Informacije o kupcu', {
            'fields': ('customer_name', 'customer_phone', 'customer_email', 'address', 'city')
        }),
        ('Status narudžbine', {
            'fields': ('status', 'notes', 'admin_notes')
        }),
        ('Finansije', {
            'fields': ('total_amount',)
        }),
        ('Notifikacije', {
            'fields': ('sms_sent', 'email_sent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'is_read', 'is_replied', 'created_at']
    list_filter = ['is_read', 'is_replied', 'created_at']
    search_fields = ['name', 'phone', 'email', 'message']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Informacije o pošiljaocu', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Poruka', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('is_read', 'is_replied')
        }),
        ('Datum', {
            'fields': ('created_at',)
        }),
    )
