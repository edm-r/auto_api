from django.contrib import admin
from .models import Category, Brand, CarModel, Product, ProductImage, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Administration des catégories"""
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Administration des marques"""
    list_display = ['name', 'country', 'is_active', 'created_at']
    list_filter = ['is_active', 'country', 'created_at']
    search_fields = ['name', 'country', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    """Administration des modèles de voitures"""
    list_display = ['name', 'brand', 'year_start', 'year_end', 'body_type', 'is_active']
    list_filter = ['brand', 'body_type', 'is_active', 'year_start']
    search_fields = ['name', 'brand__name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


class ProductImageInline(admin.TabularInline):
    """Inline pour les images des produits"""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'display_order']


class ProductVariantInline(admin.TabularInline):
    """Inline pour les variantes des produits"""
    model = ProductVariant
    extra = 1
    fields = ['name', 'sku', 'attribute_name', 'attribute_value', 'price_modifier']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Administration des produits"""
    list_display = ['name', 'sku', 'category', 'brand', 'price', 'stock_quantity', 'is_active', 'is_featured']
    list_filter = ['category', 'brand', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'discount_percentage', 'is_low_stock', 'is_in_stock']
    inlines = [ProductImageInline, ProductVariantInline]
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'sku', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'brand', 'compatible_car_models')
        }),
        ('Prix et stock', {
            'fields': ('price', 'cost', 'discount_percentage', 'stock_quantity', 'low_stock_alert', 'is_low_stock', 'is_in_stock')
        }),
        ('Détails supplémentaires', {
            'fields': ('weight', 'dimensions', 'warranty_months')
        }),
        ('État du produit', {
            'fields': ('is_active', 'is_featured', 'rating', 'number_of_reviews')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Ajoute l'utilisateur connecté comme créateur"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Administration des images des produits"""
    list_display = ['product', 'is_primary', 'display_order', 'created_at']
    list_filter = ['is_primary', 'product', 'created_at']
    search_fields = ['product__name', 'alt_text']
    readonly_fields = ['created_at']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Administration des variantes des produits"""
    list_display = ['product', 'name', 'sku', 'attribute_name', 'attribute_value', 'stock_quantity', 'is_active']
    list_filter = ['product', 'attribute_name', 'is_active', 'created_at']
    search_fields = ['product__name', 'name', 'sku']
    readonly_fields = ['created_at', 'updated_at', 'final_price']
