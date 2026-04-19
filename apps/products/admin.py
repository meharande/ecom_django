from django.contrib import admin

from .models import Menu, Brand, Category, Subcategory, Product, SKU, SKUImage

# Register your models here.
admin.site.register(Menu)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Product)
admin.site.register(SKU)
admin.site.register(SKUImage)
