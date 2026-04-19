from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.


class BaseModel(models.Model):
    desc = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_%(class)s_set"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=None, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Menu(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "menus"

    def __str__(self):
        return self.name


class Brand(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = "brands"

    def __str__(self):
        return self.name


class Category(BaseModel):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("menu", "name")
        db_table = "categories"

    def __str__(self):
        return f"{self.menu.name} → {self.name}"


class Subcategory(BaseModel):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories"
    )
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("category", "name")
        db_table = "subcategories"

    def __str__(self):
        return f"{self.category.name} → {self.name}"


class Product(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "products"

    def __str__(self):
        return self.name


class SKU(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="skus")

    sku_code = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField(default=0)
    reserved_stock = models.PositiveIntegerField(default=0)

    attributes = models.JSONField()

    class Meta:
        db_table = "product_skus"

    def __str__(self):
        return f"{self.product.name}-{self.sku_code}"


class SKUImage(BaseModel):
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="sku_images/")
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "sku_images"

    def __str__(self):
        return f"{self.sku.sku_code}-{self.image}"
