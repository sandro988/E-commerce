import re
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.

    This serializer includes validation logic to ensure data integrity and prevent circular relationships
    within the category hierarchy.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "image", "parent"]
        read_only_fields = ["slug"]

    def validate_name(self, value):
        # Checking if the category instance is being updated(for a situation where
        # user tries to update category with exact same data that it already had.)
        if self.instance:
            # If the name hasn't changed, skip validation
            if value == self.instance.name:
                return value

        # Checking if the category name contains any special characters
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "Category name cannot contain special characters."
            )

        # Checking if a category with similar name already exists (case-insensitive)
        similar_category = Category.objects.filter(name__iexact=value).first()

        if similar_category:
            raise serializers.ValidationError("category with this name already exists.")

        # Capitalize the first letter of every word in the category name
        return value.title()

    def validate_parent(self, value):
        # Preventing the category from being its own parent.
        if self.instance and value == self.instance:
            raise serializers.ValidationError("A category cannot be its own parent.")
        return value

    def validate(self, data):
        """
        Validate the data for a category.

        This method is responsible for validating the data provided for a category before it is saved.
        It performs the following checks:
        - Checks if the category instance is being updated with its own name and parent.
        In this scenario, circular relationships are not checked.
        - Checks for circular relationships in the category hierarchy.

        Parameters:
        - data (dict): The data to be validated.

        Returns:
        - dict: The validated data.

        Raises:
        - serializers.ValidationError: If the data fails validation, such as creating a circular relationship.
        (e.g. `A` is the parent of `B` and the user tries to make `B` the parent of `A`, this should not be
        allowed and should raise validation error.)
        """

        instance = self.instance
        name = data.get("name", instance.name if instance else None)
        parent = data.get("parent", instance.parent if instance else None)

        # Checking if the category instance is being updated with its own name and parent.
        # In this scenario there is no need to check for circular relationships
        if instance and name == instance.name and parent == instance.parent:
            return data

        # Checking for circular relationships
        if parent:
            current_parent = parent
            while current_parent is not None:
                if current_parent == instance:
                    raise serializers.ValidationError(
                        "This change would create a circular relationship."
                    )
                current_parent = current_parent.parent

        return data


class CategoryWithSubcategoriesSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a category with its subcategories.

    This serializer includes the basic category fields along with a list of its subcategories.
    """

    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "parent",
            "subcategories",
        ]

    def get_subcategories(self, instance):
        subcategories = instance.subcategories.all()
        serializer = CategorySerializer(subcategories, many=True)
        return serializer.data
