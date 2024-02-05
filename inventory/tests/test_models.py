import os
from django.test import TestCase
from inventory.models import Category


class CategoryModelTestClass(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Creating a parent category
        cls.parent_category = Category.objects.create(
            name="Parent Category",
            description="Description of parent category",
            image="parent_image.jpg",
        )

        # Creating a subcategory
        cls.subcategory = Category.objects.create(
            name="Subcategory",
            description="Description of subcategory",
            image="child_image.jpg",
            parent=cls.parent_category,
        )

    def test_category_string_representation(self):
        self.assertEqual(str(self.parent_category), "Parent Category")
        self.assertEqual(str(self.subcategory), "Subcategory")

    def test_category_creation(self):
        parent_category_count = Category.objects.filter(name="Parent Category").count()
        subcategory_count = Category.objects.filter(name="Subcategory").count()
        self.assertEqual(parent_category_count, 1)
        self.assertEqual(subcategory_count, 1)

    def test_category_parent_relationship(self):
        self.assertEqual(self.subcategory.parent, self.parent_category)
        self.assertEqual(self.parent_category.subcategories.first(), self.subcategory)

    def test_category_slug_generation(self):
        self.assertEqual(self.parent_category.slug, "parent-category")
        self.assertEqual(self.subcategory.slug, "subcategory")
