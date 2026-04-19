from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from apps.products.models import (
    Menu,
    Category,
    Subcategory,
    Brand,
    Product,
    SKU,
    SKUImage,
)


class Command(BaseCommand):
    help = "Seed the database with demo ecommerce data (menus, categories, brands, products, skus, images)"

    def add_arguments(self, parser):
        parser.add_argument("--products", type=int, default=20, help="Total products to create")
        parser.add_argument("--skus", type=int, default=2, help="SKUs per product")
        parser.add_argument("--images", type=int, default=2, help="Images per SKU")

    @transaction.atomic
    def handle(self, *args, **options):
        ProductCount = options["products"]
        skus_per_product = options["skus"]
        images_per_sku = options["images"]

        User = get_user_model()
        demo_user, created = User.objects.get_or_create(
            email="demo@example.com",
            defaults={
                "username": "demo",
                "is_active": True,
                "is_staff": False,
            },
        )

        self.stdout.write(self.style.SUCCESS(f"Using demo user: {demo_user.email}"))

        # Top-level menus like Amazon: Electronics, Books, Home
        menus = ["Electronics", "Books", "Home & Kitchen", "Clothing", "Toys"]
        created_menus = []
        for name in menus:
            m, _ = Menu.objects.get_or_create(name=name, creator=demo_user)
            created_menus.append(m)

        # Brands
        brand_names = [
            "Acme",
            "HyperTech",
            "GreenHome",
            "FashionCo",
            "Playtime",
        ]
        created_brands = []
        for b in brand_names:
            brand, _ = Brand.objects.get_or_create(name=b, slug=b.lower(), creator=demo_user)
            created_brands.append(brand)

        # Create categories and subcategories
        subcategories = []
        for menu in created_menus:
            for i in range(1, 4):
                cat_name = f"{menu.name} Category {i}"
                cat, _ = Category.objects.get_or_create(menu=menu, name=cat_name, creator=demo_user)
                for j in range(1, 4):
                    sub_name = f"{cat.name} Sub {j}"
                    sub, _ = Subcategory.objects.get_or_create(category=cat, name=sub_name, creator=demo_user)
                    subcategories.append(sub)

        # Create products with SKUs and images
        import random

        for idx in range(1, ProductCount + 1):
            sub = random.choice(subcategories)
            brand = random.choice(created_brands)
            product_name = f"{brand.name} Product {idx}"
            product = Product.objects.create(
                owner=demo_user,
                subcategory=sub,
                brand=brand,
                name=product_name,
                creator=demo_user,
            )

            for s in range(1, skus_per_product + 1):
                sku_code = f"SKU-{idx:04d}-{s}"
                price = round(random.uniform(5.0, 500.0), 2)
                sku = SKU.objects.create(
                    product=product,
                    sku_code=sku_code,
                    price=price,
                    stock=random.randint(0, 200),
                    reserved_stock=0,
                    attributes={"color": random.choice(["red", "blue", "green", "black", "white"]), "size": random.choice(["S","M","L","XL"])},
                    creator=demo_user,
                )

                for im in range(1, images_per_sku + 1):
                    img_path = f"sku_images/{sku_code}_{im}.jpg"
                    SKUImage.objects.create(sku=sku, image=img_path, is_primary=(im == 1), creator=demo_user)

        self.stdout.write(self.style.SUCCESS(f"Created {ProductCount} products with {skus_per_product} SKUs each."))
        self.stdout.write(self.style.SUCCESS("Seeding complete."))
