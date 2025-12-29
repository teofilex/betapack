from django.core.management.base import BaseCommand
from decimal import Decimal
from shop.models import Category, Subcategory, Product, ProductVariant, ProductImage, Order, OrderItem, ContactMessage


class Command(BaseCommand):
    help = 'Import proizvoda iz tabele - briše sve postojeće podatke i kreira nove'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Preskače potvrdu pre brisanja podataka',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('⚠️  UPOZORENJE: Ova komanda će obrisati SVE postojeće podatke iz baze!'))
        self.stdout.write(self.style.WARNING('Proizvodi, varijante, slike, narudžbine - SVE će biti obrisano.'))

        # Preskači potvrdu ako je --no-input flag postavljen
        if not options.get('no_input'):
            confirm = input('Da li želite da nastavite? (da/ne): ')
            if confirm.lower() not in ['da', 'yes', 'y']:
                self.stdout.write(self.style.ERROR('❌ Import otkazan.'))
                return
        else:
            self.stdout.write(self.style.SUCCESS('🚀 --no-input flag postavljen, preskačem potvrdu...'))

        # Brisanje svih podataka
        self.stdout.write(self.style.WARNING('🗑️  Brisanje postojećih podataka...'))

        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        ContactMessage.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        Subcategory.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('✅ Sve obrisano.'))

        # Kreiranje kategorija i podkategorija
        self.stdout.write(self.style.SUCCESS('\n📁 Kreiranje kategorija i podkategorija...'))

        # 1. Profili i Cevi
        cat_profili, _ = Category.objects.get_or_create(
            name='Profili i Cevi',
            defaults={'description': 'Firketi, flahovi i profili od kovanog gvožđa'}
        )
        subcat_firiket, _ = Subcategory.objects.get_or_create(
            name='Firiket',
            category=cat_profili,
            defaults={'description': 'Firiket profili - glatki, grifovani i upredeni'}
        )
        subcat_flahovi, _ = Subcategory.objects.get_or_create(
            name='Flahovi',
            category=cat_profili,
            defaults={'description': 'Flah profili - glatki i grifovani'}
        )
        subcat_l_profil, _ = Subcategory.objects.get_or_create(
            name='L Profili',
            category=cat_profili,
            defaults={'description': 'L profili različitih dimenzija'}
        )

        # 2. Kutije
        cat_kutije, _ = Category.objects.get_or_create(
            name='Kutije',
            defaults={'description': 'Kvadratne i pravougaone kutije'}
        )
        subcat_obicne_kutije, _ = Subcategory.objects.get_or_create(
            name='Obične kutije',
            category=cat_kutije,
            defaults={'description': 'Glatke kutije - kvadratne i pravougaone'}
        )
        subcat_grifovane_kutije, _ = Subcategory.objects.get_or_create(
            name='Grifovane kutije',
            category=cat_kutije,
            defaults={'description': 'Grifovane kutije - kvadratne i pravougaone'}
        )

        # 3. Rukohvat
        cat_rukohvat, _ = Category.objects.get_or_create(
            name='Rukohvat',
            defaults={'description': 'Rukohvati za stepenice i gelendere'}
        )

        # 4. Masnice
        cat_masnice, _ = Category.objects.get_or_create(
            name='Masnice',
            defaults={'description': 'Cevi masnice'}
        )

        # 5. Dekorativni Limovi
        cat_limovi, _ = Category.objects.get_or_create(
            name='Dekorativni Limovi',
            defaults={'description': 'Perforirani i pocinkovani limovi'}
        )

        self.stdout.write(self.style.SUCCESS(f'✅ Kreirano {Category.objects.count()} kategorija'))
        self.stdout.write(self.style.SUCCESS(f'✅ Kreirano {Subcategory.objects.count()} podkategorija'))

        # Podaci iz tabele
        products_data = {
            # Firiket gladak
            'Firiket gladak': {
                'category': cat_profili,
                'subcategory': subcat_firiket,
                'description': 'Firiket gladak profil od kovanog gvožđa, različite dimenzije',
                'base_price': 474,  # 8x8 cena kao default
                'sold_by_length': True,
                'length_per_unit': Decimal('6.0'),
                'variants': [
                    {'name': '8x8', 'price': Decimal('474')},
                    {'name': '10x10', 'price': Decimal('708')},
                    {'name': '12x12', 'price': Decimal('978')},
                    {'name': '14x14', 'price': Decimal('1254')},
                    {'name': '16x16', 'price': Decimal('1824')},
                    {'name': '20x20', 'price': Decimal('2622')},
                    {'name': '25x25', 'price': Decimal('4242')},
                    {'name': '30x30', 'price': Decimal('6012')},
                ]
            },
            # Firiket grifovan
            'Firiket grifovan': {
                'category': cat_profili,
                'subcategory': subcat_firiket,
                'description': 'Firiket grifovan profil od kovanog gvožđa, različite dimenzije',
                'base_price': 882,
                'sold_by_length': True,
                'length_per_unit': Decimal('6.0'),
                'variants': [
                    {'name': '10x10', 'price': Decimal('882')},
                    {'name': '12x12', 'price': Decimal('1080')},
                    {'name': '14x14', 'price': Decimal('1512')},
                    {'name': '16x16', 'price': Decimal('1992')},
                    {'name': '20x20', 'price': Decimal('2964')},
                    {'name': '30x30', 'price': Decimal('6498')},
                ]
            },
            # Firiket upredeni
            'Firiket upredeni': {
                'category': cat_profili,
                'subcategory': subcat_firiket,
                'description': 'Firiket upredeni profil od kovanog gvožđa, različite dimenzije',
                'base_price': 1194,
                'sold_by_length': True,
                'length_per_unit': Decimal('6.0'),
                'variants': [
                    {'name': '12x12', 'price': Decimal('1194')},
                    {'name': '14x14', 'price': Decimal('1614')},
                ]
            },
            # Flah gladak
            'Flah gladak': {
                'category': cat_profili,
                'subcategory': subcat_flahovi,
                'description': 'Flah gladak profil od kovanog gvožđa, različite dimenzije',
                'base_price': 474,
                'sold_by_length': True,
                'length_per_unit': Decimal('6.0'),
                'variants': [
                    {'name': '12x6', 'price': Decimal('474')},
                    {'name': '20x3', 'price': Decimal('426')},
                    {'name': '20x5', 'price': Decimal('684')},
                    {'name': '25x5', 'price': Decimal('804')},
                    {'name': '30x3', 'price': Decimal('576')},
                    {'name': '30x5', 'price': Decimal('996')},
                    {'name': '30x8', 'price': Decimal('1620')},
                    {'name': '40x5', 'price': Decimal('1374')},
                    {'name': '40x8', 'price': Decimal('2052')},
                    {'name': '50x5', 'price': Decimal('1650')},
                    {'name': '50x8', 'price': Decimal('2508')},
                ]
            },
            # Flah grifovan
            'Flah grifovan': {
                'category': cat_profili,
                'subcategory': subcat_flahovi,
                'description': 'Flah grifovan profil od kovanog gvožđa, različite dimenzije',
                'base_price': 594,
                'sold_by_length': True,
                'length_per_unit': Decimal('6.0'),
                'variants': [
                    {'name': '12x6', 'price': Decimal('594')},
                    {'name': '20x3', 'price': Decimal('594')},
                    {'name': '20x5', 'price': Decimal('858')},
                    {'name': '30x5', 'price': Decimal('1140')},
                    {'name': '30x8', 'price': Decimal('1794')},
                    {'name': '40x5', 'price': Decimal('1536')},
                    {'name': '40x8', 'price': Decimal('2256')},
                    {'name': '50x5', 'price': Decimal('1944')},
                ]
            },
            # L profil
            'L profil': {
                'category': cat_profili,
                'subcategory': subcat_l_profil,
                'description': 'L profil od kovanog gvožđa, različite dimenzije',
                'base_price': 1242,
                'sold_by_length': True,
                'length_per_unit': Decimal('6.0'),
                'variants': [
                    {'name': '30x30x3', 'price': Decimal('1242')},
                    {'name': '40x40x4', 'price': Decimal('2166')},
                    {'name': '50x50x5', 'price': Decimal('3846')},
                ]
            },
            # Kutija kvadratna glatka
            'Kutija kvadratna glatka': {
                'category': cat_kutije,
                'subcategory': subcat_obicne_kutije,
                'description': 'Kvadratna glatka kutija od kovanog gvožđa, različite dimenzije',
                'base_price': 840,
                'sold_by_length': True,
                'length_per_unit': Decimal('6.0'),
                'variants': [
                    {'name': '20x20x1.8', 'price': Decimal('840')},
                    {'name': '25x25x1.8', 'price': Decimal('1116')},
                    {'name': '30x30x1.8', 'price': Decimal('1308')},
                    {'name': '40x40x1.8', 'price': Decimal('1824')},
                    {'name': '40x40x2.8', 'price': Decimal('2760')},
                    {'name': '50x50x1.8', 'price': Decimal('2436')},
                    {'name': '60x60x1.8', 'price': Decimal('2970')},
                    {'name': '60x60x2.8', 'price': Decimal('4308')},
                    {'name': '80x80x1.8', 'price': Decimal('4356')},
                    {'name': '80x80x2.8', 'price': Decimal('5412')},
                    {'name': '100x100x2.8', 'price': Decimal('7122')},
                ]
            },
            # Kutija kvadratna grifovana
            'Kutija kvadratna grifovana': {
                'category': cat_kutije,
                'subcategory': subcat_grifovane_kutije,
                'description': 'Kvadratna grifovana kutija od kovanog gvožđa, različite dimenzije',
                'base_price': 1032,
                'sold_by_length': True,
                'length_per_unit': Decimal('6.0'),
                'variants': [
                    {'name': '20x20x1.8', 'price': Decimal('1032')},
                    {'name': '30x30x1.8', 'price': Decimal('1512')},
                    {'name': '40x40x1.8', 'price': Decimal('2028')},
                    {'name': '40x40x2.8', 'price': Decimal('3132')},
                    {'name': '50x50x1.8', 'price': Decimal('2568')},
                    {'name': '60x60x1.8', 'price': Decimal('3246')},
                    {'name': '60x60x2.8', 'price': Decimal('4926')},
                ]
            },
            # Kutija pravougaona glatka
            'Kutija pravougaona glatka': {
                'category': cat_kutije,
                'subcategory': subcat_obicne_kutije,
                'description': 'Pravougaona glatka kutija od kovanog gvožđa, različite dimenzije',
                'base_price': 1116,
                'sold_by_length': True,
                'length_per_unit': Decimal('6.0'),
                'variants': [
                    {'name': '30x20x1.8', 'price': Decimal('1116')},
                    {'name': '40x20x1.8', 'price': Decimal('1476')},
                    {'name': '40x30x1.8', 'price': Decimal('1512')},
                    {'name': '50x30x1.8', 'price': Decimal('1800')},
                    {'name': '60x20x1.8', 'price': Decimal('2184')},
                    {'name': '60x30x2.8', 'price': Decimal('3600')},
                    {'name': '60x40x1.8', 'price': Decimal('2280')},
                    {'name': '60x40x2.8', 'price': Decimal('3810')},
                    {'name': '80x40x1.8', 'price': Decimal('2940')},
                    {'name': '80x40x2.8', 'price': Decimal('4500')},
                    {'name': '100x40x2.8', 'price': Decimal('5364')},
                    {'name': '100x60x2.8', 'price': Decimal('5700')},
                ]
            },
            # Kutija pravougaona grifovana
            'Kutija pravougaona grifovana': {
                'category': cat_kutije,
                'subcategory': subcat_grifovane_kutije,
                'description': 'Pravougaona grifovana kutija od kovanog gvožđa, različite dimenzije',
                'base_price': 1326,
                'sold_by_length': True,
                'length_per_unit': Decimal('6.0'),
                'variants': [
                    {'name': '30x20x1.8', 'price': Decimal('1326')},
                    {'name': '40x20x1.8', 'price': Decimal('1536')},
                    {'name': '40x30x1.8', 'price': Decimal('1782')},
                    {'name': '50x30x1.8', 'price': Decimal('2280')},
                    {'name': '60x40x1.8', 'price': Decimal('2850')},
                    {'name': '60x40x2.8', 'price': Decimal('4320')},
                ]
            },
            # Rukohvat
            'Rukohvat': {
                'category': cat_rukohvat,
                'subcategory': None,
                'description': 'Rukohvat za stepenice i gelendere od kovanog gvožđa',
                'base_price': 2010,
                'sold_by_length': True,
                'length_per_unit': Decimal('6.0'),
                'variants': [
                    {'name': '30x30', 'price': Decimal('2010')},
                    {'name': '40x40', 'price': Decimal('3300')},
                ]
            },
            # Masnice
            'Masnice': {
                'category': cat_masnice,
                'subcategory': None,
                'description': 'Masnice cevi od kovanog gvožđa (prodaja po 2m)',
                'base_price': 100,
                'sold_by_length': True,
                'length_per_unit': Decimal('2.0'),  # 2m umesto 6m
                'variants': [
                    {'name': '15x1.5', 'price': Decimal('100')},
                ]
            },
            # Perforirani Lim
            'Perforirani Lim': {
                'category': cat_limovi,
                'subcategory': None,
                'description': 'Perforirani lim debljine 1mm, tabla 1000x2000mm',
                'base_price': 7200,
                'sold_by_length': False,  # Prodaja po tabeli, ne po metraži
                'length_per_unit': Decimal('1.0'),
                'variants': [
                    {'name': 'Fi 3mm', 'price': Decimal('7200')},
                    {'name': 'Fi 5mm', 'price': Decimal('7200')},
                    {'name': 'Fi 6mm', 'price': Decimal('7200')},
                    {'name': 'Fi 8mm', 'price': Decimal('7200')},
                ]
            },
            # Pocinkovani Lim
            'Pocinkovani Lim': {
                'category': cat_limovi,
                'subcategory': None,
                'description': 'Pocinkovani lim debljine 1mm, tabla 1000x2000mm',
                'base_price': 4000,
                'sold_by_length': False,  # Prodaja po tabeli, ne po metraži
                'length_per_unit': Decimal('1.0'),
                'variants': [
                    {'name': 'Krugovi (1000x2000mm)', 'price': Decimal('4000')},
                    {'name': 'Kocke 30x30 (1000x2000mm)', 'price': Decimal('4000')},
                ]
            },
        }

        # Kreiranje proizvoda i varijanti
        self.stdout.write(self.style.SUCCESS('\n📦 Kreiranje proizvoda i varijanti...'))

        total_products = 0
        total_variants = 0

        for product_name, data in products_data.items():
            # Kreiraj proizvod
            product = Product.objects.create(
                name=product_name,
                description=data['description'],
                price=data['base_price'],
                category=data['category'],
                subcategory=data['subcategory'],
                sold_by_length=data['sold_by_length'],
                length_per_unit=data['length_per_unit'],
                in_stock=True,
                stock_quantity=0,  # 0 = neograničeno
            )
            total_products += 1

            # Kreiraj varijante
            for variant_data in data['variants']:
                ProductVariant.objects.create(
                    product=product,
                    name=variant_data['name'],
                    price=variant_data['price'],
                    in_stock=True,
                    stock_quantity=0,
                )
                total_variants += 1

            self.stdout.write(f'  ✓ {product_name} ({len(data["variants"])} varijanti)')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Import završen!'))
        self.stdout.write(self.style.SUCCESS(f'📦 Kreirano {total_products} proizvoda'))
        self.stdout.write(self.style.SUCCESS(f'🎯 Kreirano {total_variants} varijanti'))
        self.stdout.write(self.style.SUCCESS(f'📁 Kreirano {Category.objects.count()} kategorija'))
        self.stdout.write(self.style.SUCCESS(f'📂 Kreirano {Subcategory.objects.count()} podkategorija'))
