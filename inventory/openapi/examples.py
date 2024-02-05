from drf_spectacular.openapi import OpenApiExample


def list_category_examples():
    """
    Provides examples for listing categories.

    Returns:
        List[OpenApiExample]: A list of response examples for listing categories.

    Example Usage:
        @extend_schema(examples=list_category_examples())
        def list(self, request, *args, **kwargs):
            pass
    """

    return [
        OpenApiExample(
            "Valid example (GET Response)",
            summary="List categories",
            description="Example of listing categories with a `GET` request.",
            value=[
                {
                    "id": 1,
                    "name": "Category1",
                    "slug": "category1",
                    "description": "Description for Category1",
                    "image": "category1_image.jpg",
                    "parent": None,
                },
                {
                    "id": 2,
                    "name": "Category2",
                    "slug": "category2",
                    "description": "Description for Category2",
                    "image": "category2_image.jpg",
                    "parent": None,
                },
            ],
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            "Valid example (GET Response) - Empty list",
            summary="List categories - Empty response",
            description="Example of listing categories when there are no categories in DB.",
            value=[],
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            "Valid example 3 (Response)",
            summary="List categories with invalid token",
            description="This example demonstrates the response after trying to list categories with invalid token.",
            value={"detail": "Invalid token."},
            response_only=True,
            status_codes=[401],
        ),
    ]


def retrieve_category_examples():
    """
    Provides examples for retrieving a category.

    Returns:
        List[OpenApiExample]: A list of response examples for retrieving a category.

    Example Usage:
        @extend_schema(examples=retrieve_category_examples())
        def retrieve(self, request, *args, **kwargs):
            pass
    """

    return [
        OpenApiExample(
            "Valid example 1 (GET Response)",
            summary="Retrieve category",
            description="Example of retrieving a category with `GET` request.",
            value={
                "id": 1,
                "name": "Some Category",
                "slug": "some-category",
                "description": "Description for the category",
                "image": "category_image.jpg",
                "parent": None,
            },
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            "Valid example 2 (GET Response)",
            summary="Retrieve category with subcategories",
            description="Example of retrieving a category alongside with its subcategories using `GET` request.",
            value={
                "id": 1,
                "name": "Some Category",
                "slug": "some-category",
                "description": "Description for the category",
                "image": "category_image.jpg",
                "parent": None,
                "subcategories": [
                    {
                        "id": 2,
                        "name": "First Subcategory",
                        "slug": "first-subcategory",
                        "description": "Description for the subcategory",
                        "image": "subcategory_image.jpg",
                        "parent": 1,
                    },
                    {
                        "id": 3,
                        "name": "Second Subcategory",
                        "slug": "second-subcategory",
                        "description": "Description for the subcategory",
                        "image": "subcategory_image.jpg",
                        "parent": 1,
                    },
                ],
            },
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            "Valid example 3 (Response)",
            summary="Retrieving category with invalid token",
            description="This example demonstrates the response after trying to retrieve a category with invalid token.",
            value={"detail": "Invalid token."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 4 (GET Response)",
            summary="Retrieve non-existing category",
            description="Example of retrieving a category that does not exist.",
            value={"detail": "Not found."},
            response_only=True,
            status_codes=[404],
        ),
    ]


def create_category_examples():
    """
    Provides examples for creating categories.

    Returns:
        List[OpenApiExample]: A list of request/response examples for creating categories.

    Example Usage:
        @extend_schema(examples=create_category_examples())
        def create(self, request, *args, **kwargs):
            pass
    """

    return [
        OpenApiExample(
            "Valid example 1 (Request)",
            summary="Creating multiple categories",
            description="This example demonstrates how to create multiple categories in a single request.",
            value=[
                {
                    "name": "Category1",
                    "description": "Description for Category1",
                    "image": None,
                    "parent": None,
                },
                {
                    "name": "Category2",
                    "description": "Description for Category2",
                    "image": None,
                    "parent": None,
                },
            ],
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 2 (Request)",
            summary="Creating single category",
            description="This example demonstrates how to create a single category in a request.",
            value={
                "name": "Category1",
                "description": "Description for Category1",
                "image": None,
                "parent": None,
            },
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 1 (Response)",
            summary="Response after creating multiple categories",
            description="This example demonstrates the response after successfully creating multiple categories.",
            value=[
                {
                    "id": 1,
                    "name": "Category1",
                    "slug": "category1",
                    "description": "Description for Category1",
                    "image": None,
                    "parent": None,
                },
                {
                    "id": 2,
                    "name": "Category2",
                    "slug": "category2",
                    "description": "Description for Category2",
                    "image": None,
                    "parent": None,
                },
            ],
            response_only=True,
        ),
        OpenApiExample(
            "Valid example 2 (Response)",
            summary="Response after category creation",
            description="This example demonstrates the response after successfully creating a single category.",
            value=[
                {
                    "id": 1,
                    "name": "Category1",
                    "description": "Description for Category1",
                    "image": None,
                    "parent": None,
                }
            ],
            response_only=True,
        ),
        OpenApiExample(
            "Valid example 3 (Response)",
            summary="Creating category with invalid data",
            description="Example of response for creating a category with invalid data.",
            value=[
                {"name": ["This field may not be blank."]},
                {"name": ["Ensure this field has no more than 128 characters."]},
                {
                    "image": [
                        "The submitted data was not a file. Check the encoding type on the form."
                    ],
                },
                {"parent": ["Incorrect type. Expected pk value, received str."]},
                {"parent": ['Invalid pk "99999" - object does not exist.']},
            ],
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 4 (Response)",
            summary="Creating category with missing fields",
            description="Example of response for creating a category with missing fields.",
            value={"name": ["This field is required."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 5 (Response)",
            summary="Creating category that already exists",
            description="Example of response for creating a category that already exists.",
            value={"name": ["category with this name already exists."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 6 (Response)",
            summary="Creating category with special characters",
            description="Example of response for creating a category with special characters.",
            value={"name": ["Category name cannot contain special characters."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 7 (Response)",
            summary="Creating category with unauthenticated user",
            description="This example demonstrates the response after trying to create a category while unauthenticated.",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 8 (Response)",
            summary="Creating category with invalid token",
            description="This example demonstrates the response after trying to create a category with invalid token.",
            value={"detail": "Invalid token."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 9 (Response)",
            summary="Creating category with insufficient permissions",
            description="This example demonstrates the response after trying to create a category with an user \
                that does not have necessary permissions.",
            value={"detail": "You do not have permission to perform this action."},
            response_only=True,
            status_codes=[403],
        ),
    ]


def update_category_examples():
    """
    Provides examples for updating categories.

    Returns:
        List[OpenApiExample]: A list of request/response examples for updating categories with `PUT` request.

    Example Usage:
        @extend_schema(examples=update_category_examples())
        def update(self, request, *args, **kwargs):
            pass
    """

    return [
        OpenApiExample(
            "Valid example (PUT Request)",
            summary="Update category",
            description="Example of updating a category with `PUT` request.",
            value={
                "name": "Updated Category",
                "description": "Updated description for the category",
                "image": "updated_image.jpg",
                "parent": 1,
            },
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 1 (PUT Response)",
            summary="Update category response",
            description="Example of response for successfully updating a category.",
            value={
                "id": 2,
                "name": "Updated Category",
                "slug": "updated-category",
                "description": "Updated description for the category",
                "image": "updated_image.jpg",
                "parent": 1,
            },
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            "Valid example 2 (PUT Response)",
            summary="Update category with invalid data",
            description="Example of response for updating a category with invalid data.",
            value={
                "name": ["Ensure this field has no more than 128 characters."],
                "image": [
                    "The submitted data was not a file. Check the encoding type on the form."
                ],
                "parent": ["Incorrect type. Expected pk value, received str."],
            },
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 3 (PUT Response)",
            summary="Update category with missing fields",
            description="Example of response for updating a category with missing fields.",
            value={
                "name": ["This field is required."],
            },
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 4 (PUT Response)",
            summary="Updating category name with category name that already exists",
            description="Example of response for updating a category name field with value that already exists.",
            value={"name": ["category with this name already exists."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 5 (PUT Response)",
            summary="Updating category parent with its own id.",
            description="Example of response for updating a category parent field with its own primary key value.",
            value={"parent": ["A category cannot be its own parent."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 6 (PUT Response)",
            summary="Updating category name with parent that does not exist",
            description="Example of response for updating a category parent field with value that does not exist.",
            value={"parent": ['Invalid pk "99999" - object does not exist.']},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 7 (PUT Response)",
            summary="Updating category name with special characters",
            description="Example of response for updating category with special characters.",
            value={"name": ["Category name cannot contain special characters."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 8 (PUT Response)",
            summary="Updating category name with circular relationship",
            description="An example of a scenario when the user tries to make a subcategory, parent of its parent, \
            thus creating a circular relationship. (e.g. `A` is the parent of `B` and the user tries to make `B` the parent of `A`)",
            value={
                "non_field_errors": [
                    "This change would create a circular relationship."
                ]
            },
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 9 (PUT Response)",
            summary="Updating category with unauthenticated user",
            description="This example demonstrates the response after trying to update a category while unauthenticated.",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 10 (PUT Response)",
            summary="Updating category with invalid token",
            description="This example demonstrates the response after trying to update a category with invalid token.",
            value={"detail": "Invalid token."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 11 (PUT Response)",
            summary="Updating category with insufficient permissions",
            description="This example demonstrates the response after trying to update a category with an user \
                that does not have necessary permissions.",
            value={"detail": "You do not have permission to perform this action."},
            response_only=True,
            status_codes=[403],
        ),
        OpenApiExample(
            "Valid example 12 (PUT Response)",
            summary="Updating category that does not exist",
            description="This example demonstrates the response after trying to update a category that does not exist.",
            value={"detail": "Not found."},
            response_only=True,
            status_codes=[404],
        ),
    ]


def partial_update_category_examples():
    """
    Provides examples for partially updating categories.

    Returns:
        List[OpenApiExample]: A list of request/response examples for partially updating categories with `PATCH` request.

    Example Usage:
        @extend_schema(examples=partial_update_category_examples())
        def partial_update(self, request, *args, **kwargs):
            pass
    """

    return [
        OpenApiExample(
            "Valid example 1 (PATCH Request)",
            summary="Update category partially",
            description="Example of partially updating a category with `PATCH` request.",
            value={
                "description": "Updated description for the category",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 1 (PATCH Response)",
            summary="Partially updated category response",
            description="Example of response for partially updating a category.",
            value={
                "id": 1,
                "name": "Some Category",
                "slug": "some-category",
                "description": "Updated description for the category",
                "image": None,
                "parent": None,
            },
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            "Valid example 2 (PATCH Response)",
            summary="Partial update category with invalid data",
            description="Example of response for partially updating a category with invalid data.",
            value={
                "name": ["Ensure this field has no more than 128 characters."],
                "image": [
                    "The submitted data was not a file. Check the encoding type on the form."
                ],
                "parent": ["Incorrect type. Expected pk value, received str."],
            },
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 3 (PATCH Response)",
            summary="Partial update category with missing fields",
            description="Example of response for partially updating a category with missing fields.",
            value={
                "name": ["This field is required."],
            },
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 4 (PATCH Response)",
            summary="Partially updating category name with category name that already exists",
            description="Example of response for updating a category name field with value that already exists.",
            value={"name": ["category with this name already exists."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 5 (PATCH Response)",
            summary="Partially updating category parent with its own id.",
            description="Example of response for partially updating a category parent field with its own primary key value.",
            value={"parent": ["A category cannot be its own parent."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 6 (PATCH Response)",
            summary="Partially updating category name with parent that does not exist",
            description="Example of response for partially updating a category parent field with value that does not exist.",
            value={"parent": ['Invalid pk "99999" - object does not exist.']},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 7 (PATCH Response)",
            summary="Partially updating category name with special characters",
            description="Example of response for partially updating category with special characters.",
            value={"name": ["Category name cannot contain special characters."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 8 (PATCH Response)",
            summary="Partially updating category name with circular relationship",
            description="An example of a scenario when the user tries to make a subcategory, parent of its parent, \
            thus creating a circular relationship. (e.g. `A` is the parent of `B` and the user tries to make `B` the parent of `A`)",
            value={
                "non_field_errors": [
                    "This change would create a circular relationship."
                ]
            },
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 9 (PATCH Response)",
            summary="Partially updating category with unauthenticated user",
            description="This example demonstrates the response after trying to partially update a category while unauthenticated.",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 10 (PATCH Response)",
            summary="Partially updating category with invalid token",
            description="This example demonstrates the response after trying to partially update a category with invalid token.",
            value={"detail": "Invalid token."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 11 (PATCH Response)",
            summary="Partially updating category with insufficient permissions",
            description="This example demonstrates the response after trying to partially update a category with an user that does not have necessary permissions.",
            value={"detail": "You do not have permission to perform this action."},
            response_only=True,
            status_codes=[403],
        ),
        OpenApiExample(
            "Valid example 12 (PATCH Response)",
            summary="Partially updating category that does not exist",
            description="This example demonstrates the response after trying to partially update a category that does not exist.",
            value={"detail": "Not found."},
            response_only=True,
            status_codes=[404],
        ),
    ]


def delete_category_examples():
    """
    Provides examples for deleting categories.

    Returns:
        List[OpenApiExample]: A list of response examples for deleting categories.

    Example Usage:
        @extend_schema(examples=delete_category_examples())
        def destroy(self, request, *args, **kwargs):
            pass
    """

    return [
        OpenApiExample(
            "Valid example 1 (DELETE Response)",
            summary="Deleted category response",
            description="Example of response for successfully deleting a category.",
            value=None,  # No response body for DELETE request
            response_only=True,
            status_codes=[204],
        ),
        OpenApiExample(
            "Valid example 2 (DELETE Response)",
            summary="Deleting category with unauthenticated user",
            description="This example demonstrates the response after trying to delete a category while unauthenticated.",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 3 (DELETE Response)",
            summary="Deleting category with invalid token",
            description="This example demonstrates the response after trying to delete a category with invalid token.",
            value={"detail": "Invalid token."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 4 (DELETE Response)",
            summary="Deleting category with insufficient permissions",
            description="This example demonstrates the response after trying to delete a category with an user that does not have necessary permissions.",
            value={"detail": "You do not have permission to perform this action."},
            response_only=True,
            status_codes=[403],
        ),
        OpenApiExample(
            "Valid example 5 (DELETE Response)",
            summary="Trying to delete a category that does not exist",
            description="This example demonstrates the response after trying to delete a category that does not exist.",
            value={"detail": "Not found."},
            response_only=True,
            status_codes=[404],
        ),
    ]
