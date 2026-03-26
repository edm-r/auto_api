from rest_framework import serializers
from .models import Category, Brand, CarModel, Product, ProductImage, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories"""
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def validate_name(self, value):
        """Valide le nom unique"""
        if Category.objects.filter(name__iexact=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("Une catégorie avec ce nom existe déjà.")
        return value


class BrandSerializer(serializers.ModelSerializer):
    """Serializer pour les marques"""
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description', 'logo',
            'country', 'website', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def validate_name(self, value):
        """Valide le nom unique"""
        if Brand.objects.filter(name__iexact=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("Une marque avec ce nom existe déjà.")
        return value

    def validate_website(self, value):
        """Valide l'URL du site web"""
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("L'URL doit commencer par http:// ou https://")
        return value


class CarModelSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les modèles de voitures (dans les listes)"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = CarModel
        fields = ['id', 'brand', 'brand_name', 'name', 'year_start', 'year_end', 'body_type']
        read_only_fields = ['id']


class CarModelSerializer(serializers.ModelSerializer):
    """Serializer complet pour les modèles de voitures"""
    brand_detail = BrandSerializer(source='brand', read_only=True)
    
    class Meta:
        model = CarModel
        fields = [
            'id', 'brand', 'brand_detail', 'name', 'slug', 
            'year_start', 'year_end', 'body_type', 'image',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def validate(self, data):
        """Valide que year_end >= year_start"""
        year_start = data.get('year_start', self.instance.year_start if self.instance else None)
        year_end = data.get('year_end', self.instance.year_end if self.instance else None)
        
        if year_end and year_start and year_end < year_start:
            raise serializers.ValidationError(
                "L'année de fin doit être supérieure ou égale à l'année de début."
            )
        
        return data


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer pour les images de produits"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'alt_text', 'is_primary', 'display_order', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductImageDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les images avec URL complète"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'display_order']
        read_only_fields = ['id']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer pour les variantes de produits"""
    final_price = serializers.DecimalField(
        read_only=True, 
        max_digits=10, 
        decimal_places=2
    )
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'name', 'sku', 'attribute_name',
            'attribute_value', 'price_modifier', 'final_price',
            'stock_quantity', 'is_in_stock', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_sku(self, value):
        """Valide le SKU unique"""
        if ProductVariant.objects.filter(sku=value).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError("Ce SKU existe déjà.")
        return value


class ProductSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les produits (listes)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category', 'category_name',
            'brand', 'brand_name', 'price', 'stock_quantity',
            'is_in_stock', 'rating', 'is_featured', 'is_active', 'primary_image'
        ]
        read_only_fields = ['id', 'is_in_stock', 'rating']

    def get_primary_image(self, obj):
        """Récupère l'URL de l'image principale"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageDetailSerializer(primary_image).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour un produit"""
    category_detail = CategorySerializer(source='category', read_only=True)
    brand_detail = BrandSerializer(source='brand', read_only=True)
    compatible_car_models = CarModelSimpleSerializer(many=True, read_only=True)
    compatible_car_models_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=CarModel.objects.all(),
        source='compatible_car_models'
    )
    images = ProductImageDetailSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.FloatField(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'sku',
            'category', 'category_detail', 'brand', 'brand_detail',
            'compatible_car_models', 'compatible_car_models_ids',
            'price', 'cost', 'discount_percentage',
            'stock_quantity', 'is_in_stock', 'is_low_stock',
            'low_stock_alert', 'weight', 'dimensions',
            'warranty_months', 'is_active', 'is_featured',
            'rating', 'number_of_reviews',
            'images', 'variants',
            'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'is_in_stock', 'is_low_stock',
            'rating', 'number_of_reviews',
            'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]

    def validate_sku(self, value):
        """Valide le SKU unique"""
        if Product.objects.filter(sku=value).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError("Ce SKU existe déjà.")
        return value

    def validate_name(self, value):
        """Valide le nom"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Le nom du produit ne peut pas être vide.")
        return value

    def validate(self, data):
        """Validations au niveau de l'objet"""
        # Vérifie que le prix de vente > coût de revient
        price = data.get('price', self.instance.price if self.instance else None)
        cost = data.get('cost', self.instance.cost if self.instance else None)
        
        if cost and price and cost > price:
            raise serializers.ValidationError(
                "Le prix de vente doit être supérieur au coût de revient."
            )
        
        # Vérifie que stock_quantity >= 0
        stock = data.get('stock_quantity', self.instance.stock_quantity if self.instance else None)
        if stock is not None and stock < 0:
            raise serializers.ValidationError(
                "La quantité en stock ne peut pas être négative."
            )
        
        return data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier les produits"""
    compatible_car_models_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=CarModel.objects.all(),
        source='compatible_car_models',
        required=False,
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'sku', 'category', 'brand',
            'compatible_car_models_ids', 'price', 'cost',
            'stock_quantity', 'low_stock_alert', 'weight',
            'dimensions', 'warranty_months', 'is_active', 'is_featured'
        ]

    def validate_sku(self, value):
        """Valide le SKU unique"""
        if Product.objects.filter(sku=value).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError("Ce SKU existe déjà.")
        return value

    def create(self, validated_data):
        """Crée le produit avec l'utilisateur connecté"""
        created_by = validated_data.pop('created_by', None)
        compatible_car_models = validated_data.pop('compatible_car_models', [])
        if created_by is None:
            request = self.context.get('request')
            created_by = getattr(request, 'user', None) if request is not None else None

        product = Product.objects.create(created_by=created_by, **validated_data)
        product.compatible_car_models.set(compatible_car_models)
        return product


class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer pour lister les catégories avec nombre de produits"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'is_active', 'product_count']

    def get_product_count(self, obj):
        """Compte le nombre de produits actifs dans la catégorie"""
        return obj.products.filter(is_active=True).count()
