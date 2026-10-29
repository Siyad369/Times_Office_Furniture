from django.core.management.base import BaseCommand
from product.models import Category


class Command(BaseCommand):
    help = "Create the default furniture categories"

    def handle(self, *args, **options):
        categories = [
            "Sofa",
            "Office Chair",
            "Visitors Chair",
            "Plastic Chairs",
            "Cafe Chairs",
            "Normal Tables",
            "Tea Poy",
            "Executive Tables",
            "Wardrobes",
        ]

        for name in categories:
            category, created = Category.objects.get_or_create(
                name=name
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created category: {name}"
                    )
                )
            else:
                self.stdout.write(
                    f"Category already exists: {name}"
                )

        self.stdout.write(
            self.style.SUCCESS("Category seeding completed.")
        )