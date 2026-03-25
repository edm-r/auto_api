from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.contrib.auth.models import User


class Category(models.Model):
    """
    Catégories de pièces détachées (moteur, freins, suspension, etc.)
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nom de la catégorie"
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text="URL-friendly version du nom"
    )
    description = models.TextField(
        blank=True,
        help_text="Description de la catégorie"
    )
    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True,
        help_text="Image de la catégorie"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="La catégorie est-elle active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    """
    Marques automobiles (Peugeot, Renault, Citroën, etc.)
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nom de la marque"
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text="URL-friendly version du nom"
    )
    description = models.TextField(
        blank=True,
        help_text="Description de la marque"
    )
    logo = models.ImageField(
        upload_to='brands/',
        null=True,
        blank=True,
        help_text="Logo de la marque"
    )
    country = models.CharField(
        max_length=50,
        blank=True,
        help_text="Pays d'origine"
    )
    website = models.URLField(
        blank=True,
        help_text="Site web de la marque"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="La marque est-elle active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CarModel(models.Model):
    """
    Modèles automobiles (308, Megane, Berlingo, etc.)
    """
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='car_models',
        help_text="Marque du véhicule"
    )
    name = models.CharField(
        max_length=100,
        help_text="Nom du modèle"
    )
    slug = models.SlugField(
        null=True,
        blank=True,
        help_text="URL-friendly version du nom"
    )
    year_start = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
        help_text="Année de début de production"
    )
    year_end = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
        help_text="Année de fin de production"
    )
    body_type = models.CharField(
        max_length=50,
        choices=[
            ('sedan', 'Berline'),
            ('coupe', 'Coupé'),
            ('suv', 'SUV'),
            ('hatchback', 'Monospace'),
            ('station_wagon', 'Break'),
            ('van', 'Fourgonnette'),
            ('truck', 'Camion'),
            ('other', 'Autre'),
        ],
        default='sedan',
        help_text="Type de carrosserie"
    )
    image = models.ImageField(
        upload_to='car_models/',
        null=True,
        blank=True,
        help_text="Image du modèle"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Le modèle est-il actif?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year_start', 'name']
        unique_together = ['brand', 'name', 'year_start']
        verbose_name = 'Car Model'
        verbose_name_plural = 'Car Models'
        indexes = [
            models.Index(fields=['brand', 'name']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"{self.brand.name} {self.name} ({self.year_start}-{self.year_end or 'present'})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.name}")
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Produits (pièces détachées)
    """
    # Informations générales
    name = models.CharField(
        max_length=200,
        help_text="Nom du produit"
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text="URL-friendly version du nom"
    )
    description = models.TextField(
        help_text="Description détaillée du produit"
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        help_text="Stock Keeping Unit (référence du produit)"
    )
    
    # Classification
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        help_text="Catégorie du produit"
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        help_text="Marque du produit (fabricant)"
    )
    compatible_car_models = models.ManyToManyField(
        CarModel,
        related_name='products',
        blank=True,
        help_text="Modèles de voitures compatibles"
    )
    
    # Prix et stock
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Prix unitaire de base"
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text="Coût de revient"
    )
    low_stock_alert = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Seuil d'alerte de stock bas"
    )
    
    # Détails supplémentaires
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Poids en kg"
    )
    dimensions = models.CharField(
        max_length=255,
        blank=True,
        help_text="Dimensions (L x l x H)"
    )
    warranty_months = models.IntegerField(
        default=12,
        validators=[MinValueValidator(0)],
        help_text="Durée de garantie en mois"
    )
    
    # État du produit
    is_active = models.BooleanField(
        default=True,
        help_text="Le produit est-il actif?"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Produit en vedette?"
    )
    
    # Métadonnées
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Note moyenne (0-5)"
    )
    number_of_reviews = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Nombre d'avis clients"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_created'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def stock_quantity(self):
        """Calcul dynamique du stock total selon l'inventaire"""
        return sum(inv.quantity for inv in self.inventories.all())

    @property
    def is_low_stock(self):
        """Vérifie si le stock total est bas"""
        return self.stock_quantity <= self.low_stock_alert

    @property
    def is_in_stock(self):
        """Vérifie si le produit est en stock"""
        return self.stock_quantity > 0

    @property
    def discount_percentage(self):
        """Calcule le pourcentage de marge"""
        if self.cost and self.price > 0:
            return round(((self.price - self.cost) / self.price) * 100, 2)
        return 0


class ProductImage(models.Model):
    """
    Images des produits
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="Produit associé"
    )
    image = models.ImageField(
        upload_to='products/',
        help_text="Image du produit"
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Texte alternatif pour l'image"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Image principale du produit?"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Ordre d'affichage"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'created_at']
        verbose_name_plural = 'Product Images'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['is_primary']),
        ]

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule image primaire par produit
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """
    Variantes de produits (couleur, taille, version, etc.)
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        help_text="Produit parent"
    )
    
    # Informations de variante
    name = models.CharField(
        max_length=100,
        help_text="Nom de la variante (ex: Noir, Taille M)"
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        help_text="SKU de la variante"
    )
    attribute_name = models.CharField(
        max_length=50,
        choices=[
            ('color', 'Couleur'),
            ('size', 'Taille'),
            ('version', 'Version'),
            ('material', 'Matière'),
            ('fit', 'Ajustement'),
            ('strength', 'Puissance'),
            ('other', 'Autre'),
        ],
        default='other',
        help_text="Type d'attribut"
    )
    attribute_value = models.CharField(
        max_length=100,
        help_text="Valeur de l'attribut"
    )
    
    # Prix et stock
    price_modifier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Modification de prix par rapport au produit principal"
    )
    
    # Métadonnées
    is_active = models.BooleanField(
        default=True,
        help_text="La variante est-elle disponible?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['attribute_name', 'attribute_value']
        unique_together = ['product', 'attribute_value']
        verbose_name_plural = 'Product Variants'
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def final_price(self):
        """Calcule le prix final de la variante"""
        return self.product.price + self.price_modifier

    @property
    def stock_quantity(self):
        return sum(inv.quantity for inv in self.inventories.all())

    @property
    def is_in_stock(self):
        """Vérifie si la variante est en stock"""
        return self.stock_quantity > 0


class Warehouse(models.Model):
    """
    Entrepôt de stockage.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nom de l'entrepôt"
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Adresse ou localisation de l'entrepôt"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Inventory(models.Model):
    """
    Stock disponible pour un produit/variante dans un entrepôt spécifique.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventories',
        null=True,
        blank=True,
        help_text="Produit principal"
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='inventories',
        null=True,
        blank=True,
        help_text="Variante du produit (si applicable)"
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='inventories',
        help_text="Entrepôt"
    )
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Quantité physique disponible"
    )
    reserved_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Quantité réservée par des commandes non finalisées"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['warehouse', 'product', 'variant']]
        verbose_name_plural = 'Inventories'

    def __str__(self):
        target = self.variant if self.variant else self.product
        return f"{self.warehouse.name} - {target}: {self.quantity}"

    @property
    def available_quantity(self):
        return max(0, self.quantity - self.reserved_quantity)


class StockMovement(models.Model):
    """
    Historique des mouvements de stock.
    """
    class MovementType(models.TextChoices):
        IN = 'IN', 'Entrée'
        OUT = 'OUT', 'Sortie'
        ADJUSTMENT = 'ADJUSTMENT', 'Ajustement manuel'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        null=True,
        blank=True
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        null=True,
        blank=True
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stock_movements'
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
        help_text="Type de mouvement"
    )
    quantity = models.IntegerField(
        help_text="Quantité (positive pour IN, négative pour OUT)"
    )
    reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Référence externe (Order ID, cause d'ajustement...)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = "+" if self.quantity > 0 else ""
        return f"{self.get_movement_type_display()} {sign}{self.quantity} ({self.warehouse.name})"
