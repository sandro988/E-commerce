from django.contrib import admin
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "short_description", "has_image", "parent"]
    search_fields = ["name", "description"]

    @admin.display(description="Description")
    def short_description(self, obj):
        """
        Custom method that will display a shortened version of the description.
        """
        max_length = 50
        return (
            (obj.description[:max_length] + "...")
            if len(obj.description) > max_length
            else obj.description
        )

    @admin.display(description="Image", boolean=True)
    def has_image(self, obj):
        """
        Custom method that will display if category has image or not.
        """
        return True if obj.image else False


admin.site.register(Category, CategoryAdmin)
