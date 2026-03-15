"""Management command to seed sample SyraBand products."""

from django.core.management.base import BaseCommand
from store.models import SyraBand, SyraBandType, SyraBandUse


class Command(BaseCommand):
    help = "Seed the store with sample SyraBand products"

    def handle(self, *args, **options):
        # Create band types if they don't exist
        band_types = [
            (
                "classic",
                "Classic",
                "السوار الأساسي للاستخدام اليومي. مصنوع من سيليكون طبي مريح وخفيف ومقاوم للماء. يحتوي على QR Code دائم لعرض الملف الطبي بسرعة.",
            ),
            (
                "sport",
                "Sport",
                "سوار مصمم للأنشطة الرياضية والحركة. مرن يتحمل العرق والمياه والحركة المستمرة.",
            ),
            (
                "kids",
                "Kids",
                "سوار مخصص للأطفال. يساعد في حماية الأطفال في حالات الطوارئ أو عند الضياع.",
            ),
            (
                "premium",
                "Premium",
                "النسخة الفاخرة من السوار. مصنوع من معدن عالي الجودة مع نقش ليزر دائم.",
            ),
        ]

        for type_code, type_name, desc in band_types:
            SyraBandType.objects.update_or_create(
                name=type_code, defaults={"description": desc, "is_active": True}
            )

        # Create use cases if they don't exist
        use_cases = [
            ("personal", "Personal Health", "fa-user"),
            ("child", "Child Safety", "fa-child"),
            ("athlete", "Athletes", "fa-running"),
            ("patient", "Patients", "fa-heartbeat"),
        ]

        for use_code, use_name, icon in use_cases:
            SyraBandUse.objects.update_or_create(
                name=use_code,
                defaults={
                    "description": f"Band for {use_name}",
                    "icon": icon,
                    "is_active": True,
                },
            )

        # Sample products data - SYRA Bracelets
        products = [
            # SYRA Classic - Adult sizes
            {
                "sku": "SYRA-CLS-BLK-ADT",
                "name": "SYRA Classic Black",
                "short_description": "السوار الأساسي للاستخدام اليومي",
                "description": """SYRA Classic - السوار الأساسي للاستخدام اليومي.

المميزات:
- سيليكون طبي مريح
- مقاوم للمياه
- خفيف الوزن
- QR Code دائم
- يعمل مع أي هاتف بكاميرا

مناسب لـ:
مرضى السكر، مرضى القلب، كبار السن، والأطفال.

نص السوار:
SYRA
Medical ID
Scan QR

محتويات العلبة:
- السوار
- QR Code
- تعليمات التفعيل

رسالة داخل العلبة:
Your medical identity
Always with you""",
                "band_type": "classic",
                "band_use": "personal",
                "size": "adult",
                "color": "black",
                "material": "silicone",
                "price": 299.00,
                "stock_quantity": 100,
                "is_featured": True,
            },
            {
                "sku": "SYRA-CLS-RED-ADT",
                "name": "SYRA Classic Red",
                "short_description": "السوار الأساسي للاستخدام اليومي",
                "description": """SYRA Classic - النسخة الأحمر الطبي.

المميزات:
- سيليكون طبي مريح
- مقاوم للمياه
- خفيف الوزن
- QR Code دائم
- لون أحمر طبي واضح للطوارئ

مناسب لـ:
مرضى السكر، مرضى القلب، كبار السن، والأطفال.

نص السوار:
SYRA
Medical ID
Scan QR""",
                "band_type": "classic",
                "band_use": "personal",
                "size": "adult",
                "color": "red",
                "material": "silicone",
                "price": 299.00,
                "stock_quantity": 80,
            },
            {
                "sku": "SYRA-CLS-ORG-ADT",
                "name": "SYRA Classic Orange",
                "short_description": "السوار الأساسي للاستخدام اليومي",
                "description": """SYRA Classic - لون برتقالي طوارئ.

المميزات:
- سيليكون طبي مريح
- مقاوم للمياه
- لون برتقالي واضح للطوارئ
- QR Code دائم

نص السوار:
SYRA
Medical ID
Scan QR""",
                "band_type": "classic",
                "band_use": "personal",
                "size": "adult",
                "color": "orange",
                "material": "silicone",
                "price": 299.00,
                "stock_quantity": 70,
            },
            {
                "sku": "SYRA-CLS-BLU-ADT",
                "name": "SYRA Classic Blue",
                "short_description": "السوار الأساسي للاستخدام اليومي",
                "description": """SYRA Classic - اللون الأزرق.

مريح ومقاوم للماء مع QR Code دائم.

نص السوار:
SYRA
Medical ID
Scan QR""",
                "band_type": "classic",
                "band_use": "personal",
                "size": "adult",
                "color": "blue",
                "material": "silicone",
                "price": 299.00,
                "stock_quantity": 60,
            },
            {
                "sku": "SYRA-CLS-GRN-ADT",
                "name": "SYRA Classic Green",
                "short_description": "السوار الأساسي للاستخدام اليومي",
                "description": """SYRA Classic - اللون الأخضر.

سوار طبي يومي مريح مع QR Code دائم.

نص السوار:
SYRA
Medical ID
Scan QR""",
                "band_type": "classic",
                "band_use": "personal",
                "size": "adult",
                "color": "green",
                "material": "silicone",
                "price": 299.00,
                "stock_quantity": 50,
            },
            # SYRA Sport - Adult sizes
            {
                "sku": "SYRA-SPT-ORG-ADT",
                "name": "SYRA Sport Orange",
                "short_description": "سوار مصمم للأنشطة الرياضية",
                "description": """SYRA Sport - سوار مصمم للأنشطة الرياضية والحركة.

المميزات:
- سيليكون رياضي مرن
- مقاوم للعرق والمياه
- خفيف جداً
- قراءة QR سريعة

مناسب لـ:
العدائين، الرياضيين، راكبي الدراجات، الرحلات.

نص السوار:
SYRA
Emergency Medical ID
Scan QR""",
                "band_type": "sport",
                "band_use": "athlete",
                "size": "adult",
                "color": "orange",
                "material": "silicone",
                "price": 349.00,
                "stock_quantity": 60,
            },
            {
                "sku": "SYRA-SPT-RED-ADT",
                "name": "SYRA Sport Red",
                "short_description": "سوار مصمم للأنشطة الرياضية",
                "description": """SYRA Sport - اللون الأحمر الرياضي.

سوار مرن يتحمل العرق والمياه والحركة المستمرة.

نص السوار:
SYRA
Emergency Medical ID
Scan QR""",
                "band_type": "sport",
                "band_use": "athlete",
                "size": "adult",
                "color": "red",
                "material": "silicone",
                "price": 349.00,
                "stock_quantity": 50,
            },
            {
                "sku": "SYRA-SPT-BLK-ADT",
                "name": "SYRA Sport Black",
                "short_description": "سوار مصمم للأنشطة الرياضية",
                "description": """SYRA Sport - اللون الأسود.

سوار رياضي عصري للتحرك والنشاط.

نص السوار:
SYRA
Emergency Medical ID
Scan QR""",
                "band_type": "sport",
                "band_use": "athlete",
                "size": "adult",
                "color": "black",
                "material": "silicone",
                "price": 349.00,
                "stock_quantity": 55,
            },
            # SYRA Kids - Kids sizes
            {
                "sku": "SYRA-KID-RED-KID",
                "name": "SYRA Kids Red",
                "short_description": "سوار مخصص للأطفال",
                "description": """SYRA Kids - سوار مخصص للأطفال.

المميزات:
- مقاس خاص بالأطفال
- سيليكون آمن وناعم
- ألوان جذابة
- QR مرتبط ببيانات الطفل

مناسب لـ:
الأطفال، الرحلات المدرسية، الأطفال الذين يعانون من الحساسية.

نص السوار:
SYRA
Child Medical ID
Scan QR""",
                "band_type": "kids",
                "band_use": "child",
                "size": "kids",
                "color": "red",
                "material": "silicone",
                "price": 249.00,
                "stock_quantity": 40,
            },
            {
                "sku": "SYRA-KID-ORG-KID",
                "name": "SYRA Kids Orange",
                "short_description": "سوار مخصص للأطفال",
                "description": """SYRA Kids - لون برتقالي للأطفال.

سوار آمن للأطفال مع QR مرتبط ببيانات الطفل.

نص السوار:
SYRA
Child Medical ID
Scan QR""",
                "band_type": "kids",
                "band_use": "child",
                "size": "kids",
                "color": "orange",
                "material": "silicone",
                "price": 249.00,
                "stock_quantity": 35,
            },
            {
                "sku": "SYRA-KID-BLU-KID",
                "name": "SYRA Kids Blue",
                "short_description": "سوار مخصص للأطفال",
                "description": """SYRA Kids - لون أزرق للأطفال.

سوار حماية للأطفال في حالات الطوارئ.

نص السوار:
SYRA
Child Medical ID
Scan QR""",
                "band_type": "kids",
                "band_use": "child",
                "size": "kids",
                "color": "blue",
                "material": "silicone",
                "price": 249.00,
                "stock_quantity": 30,
            },
            {
                "sku": "SYRA-KID-GRN-KID",
                "name": "SYRA Kids Green",
                "short_description": "سوار مخصص للأطفال",
                "description": """SYRA Kids - لون أخضر للأطفال.

سوار طبي آمن للأطفال.

نص السوار:
SYRA
Child Medical ID
Scan QR""",
                "band_type": "kids",
                "band_use": "child",
                "size": "kids",
                "color": "green",
                "material": "silicone",
                "price": 249.00,
                "stock_quantity": 25,
            },
            # SYRA Premium - Adult sizes (Stainless Steel)
            {
                "sku": "SYRA-PRM-SLV-ADT",
                "name": "SYRA Premium Silver",
                "short_description": "النسخة الفاخرة من السوار",
                "description": """SYRA Premium - النسخة الفاخرة من السوار.

المميزات:
- ستانلس ستيل
- نقش ليزر دائم
- QR Code محفور
- تصميم فاخر

مناسب لـ:
الاستخدام اليومي الأنيق والأشخاص الذين يفضلون الإكسسوارات المعدنية.

نص السوار:
SYRA
Medical ID
Emergency Profile
Scan QR""",
                "band_type": "premium",
                "band_use": "personal",
                "size": "adult",
                "color": "blue",
                "material": "stainless_steel",
                "price": 599.00,
                "stock_quantity": 30,
                "is_featured": True,
            },
            {
                "sku": "SYRA-PRM-GLD-ADT",
                "name": "SYRA Premium Gold",
                "short_description": "النسخة الفاخرة من السوار",
                "description": """SYRA Premium - النسخة الذهبية الفاخرة.

سوار أنيق من ستانلس ستيل مع نقش ليزر دائم.

نص السوار:
SYRA
Medical ID
Emergency Profile
Scan QR""",
                "band_type": "premium",
                "band_use": "personal",
                "size": "adult",
                "color": "orange",
                "material": "stainless_steel",
                "price": 599.00,
                "stock_quantity": 20,
            },
            {
                "sku": "SYRA-PRM-BLK-ADT",
                "name": "SYRA Premium Black",
                "short_description": "النسخة الفاخرة من السوار",
                "description": """SYRA Premium - النسخة السوداء الأنيقة.

سوار معدني فاخر بتصميم عصري.

نص السوار:
SYRA
Medical ID
Emergency Profile
Scan QR""",
                "band_type": "premium",
                "band_use": "personal",
                "size": "adult",
                "color": "black",
                "material": "stainless_steel",
                "price": 599.00,
                "stock_quantity": 25,
            },
        ]

        # Clear existing products first to avoid conflicts
        SyraBand.objects.all().delete()

        created_count = 0
        for prod_data in products:
            band_type = SyraBandType.objects.get(name=prod_data["band_type"])
            band_use = SyraBandUse.objects.get(name=prod_data["band_use"])

            SyraBand.objects.create(
                sku=prod_data["sku"],
                name=prod_data["name"],
                short_description=prod_data.get("short_description", ""),
                description=prod_data["description"],
                band_type=band_type,
                band_use=band_use,
                size=prod_data["size"],
                color=prod_data["color"],
                material=prod_data["material"],
                price=prod_data["price"],
                stock_quantity=prod_data["stock_quantity"],
                is_active=True,
                is_featured=prod_data.get("is_featured", False),
            )
            created_count += 1
            self.stdout.write(f'Created: {prod_data["name"]}')

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully seeded {created_count} products!")
        )
        self.stdout.write(f"Total products in store: {SyraBand.objects.count()}")
