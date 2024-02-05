from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """
    Model representing a category in the E-commerce platform.

    Attributes:
        name (str): The name of the category.
        slug (str): The URL-friendly slug generated from the name.
        description (str): Optional description of the category.
        image (str): The filename of the image representing the category.
        parent (Category): The parent category, creating a hierarchical relationship, this field is optional.
    """

    def category_image_filename(self, filename):
        return f"category_images/{filename}"

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=category_image_filename, blank=True, null=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        # Generates slug automatically from the category name
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
