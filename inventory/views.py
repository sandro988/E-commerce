from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from openapi.category_examples import (
    list_category_examples,
    list_subcategories_examples,
    retrieve_category_examples,
    create_category_examples,
    update_category_examples,
    partial_update_category_examples,
    delete_category_examples,
)
from .serializers import CategorySerializer, SubCategorySerializer
from .models import Category


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

    def get_serializer_class(self):
        """
        Determine the serializer class to use for this view.

        Returns the serializer class based on the action being performed.

        If the action is 'list_subcategories', returns the 'SubCategorySerializer'. Otherwise, returns the 'CategorySerializer'.

        The difference between 'SubCategorySerializer' and 'CategorySerializer' is that the former will
        return subcategories of category in response.

        Returns:
            Class: The serializer class to be used for the view.
        """

        return (
            SubCategorySerializer
            if self.action == "list_subcategories"
            else CategorySerializer
        )

    def get_permissions(self):
        """
        Returns the list of permissions for the view.

        For the 'list', 'list_subcategories' and 'retrieve' actions, permissions are set to allow any user
        to access the endpoint without authentication or specific permissions. For
        other actions, such as 'create', 'update', 'delete', only the users with is_staff
        set to True are allowed access.

        Returns:
        - List of permission classes based on the action being performed.
        """
        if self.action in ["list", "retrieve", "list_subcategories"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @extend_schema(
        responses={
            200: CategorySerializer(many=True),
            401: CategorySerializer(many=True),
        },
        examples=list_category_examples(),
    )
    def list(self, request, *args, **kwargs):
        """
        ## List all categories.

        This endpoint allows users to retrieve a list of all available categories.
        This endpoint can be accessed by **unauthenticated** users or users who do not have
        **permissions** to **create**, **update**, or **delete** categories. However, they will only
        have **read-only** access to this endpoint. **Also requests made with invalid token will receive
        401 status code**.

        ### Responses:
        - 200: Successfully retrieved the list of categories. Returns a list of category objects.
        - 401: Unauthorized. Authentication credentials were invalid.
        - *For more information about responses please check response examples in swagger.*
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: SubCategorySerializer,
            401: SubCategorySerializer,
            404: SubCategorySerializer,
        },
        examples=list_subcategories_examples(),
    )
    @action(detail=True, methods=["GET"], url_name="subcategories-list")
    def list_subcategories(self, request, *args, **kwargs):
        """
        ## List the subcategories of a category.

        This endpoint allows users to list the subcategories of an existing category identified by its slug.
        This endpoint can be accessed by **unauthenticated** users or users who do not have
        **permissions** to **create**, **update**, or **delete** categories. **Requests made with invalid token
        will receive 401 status code**.

        ### Path Parameters:
        - `slug`: The unique slug of the category whose subcategories are to be listed.

        ### Responses:
        - 200: Successfully listed the subcategories of the category. Returns a list of subcategory objects.
        - 401: Unauthorized. Trying to make a request with invalid token.
        - 404: Not found. The requested category does not exist.
        - *For more information about responses please check response examples in swagger.*
        """

        subcategories = self.get_object().subcategories
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses={
            200: CategorySerializer,
            401: CategorySerializer,
            404: CategorySerializer,
        },
        examples=retrieve_category_examples(),
    )
    def retrieve(self, request, *args, **kwargs):
        """
        ## Retrieve a category.

        This endpoint allows users to retrieve an existing category identified by its slug.
        This endpoint can be accessed by **unauthenticated** users or users who do not have
        **permissions** to **create**, **update**, or **delete** categories. **Requests made
        with invalid token will receive 401 status code**.

        ### Path Parameters:
        - `slug`: The unique slug of the category to be retrieved.

        ### Responses:
        - 200: The category was successfully retrieved. Returns the details of the category.
        - 401: Unauthorized. Trying to make a request with invalid token.
        - 404: Not found. The requested category does not exist.
        - *For more information about responses please check response examples in swagger.*
        """
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        responses={
            201: CategorySerializer,
            400: CategorySerializer,
            401: CategorySerializer,
            403: CategorySerializer,
        },
        examples=create_category_examples(),
    )
    def create(self, request, *args, **kwargs):
        """
        ## Creates a new category or multiple categories.

        This endpoint allows users to create new categories. Categories can be created either individually
        by providing a single JSON object representing the category, or in bulk by providing a list of JSON
        objects, each representing a category.

        ### Request body:
        - If creating a **single** category, provide the category data as a JSON object in the request body.
        - If creating **multiple** categories, provide a list of categories as JSON objects in the request body.
        - *For more information about requests please check request examples in swagger.*

        ### Responses:
        - 201: A category or multiple categories were successfully created. Returns the created category or categories.
        - 400: Bad request. The request body is invalid, duplicate or missing required fields.
        - 401: Unauthorized. Authentication credentials were not provided or are invalid.
        - 403: Forbidden. The user does not have permission to create categories.
        - *For more information about responses please check response examples in swagger.*
        """

        if isinstance(request.data, list):
            categories_data = request.data
            serializer = self.get_serializer(data=categories_data, many=True)
        else:
            categories_data = [request.data]
            serializer = self.get_serializer(data=categories_data, many=True)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        responses={
            200: CategorySerializer,
            400: CategorySerializer,
            401: CategorySerializer,
            403: CategorySerializer,
            404: CategorySerializer,
        },
        examples=update_category_examples(),
    )
    def update(self, request, *args, **kwargs):
        """
        ## Update an existing category.

        This endpoint allows users to update an existing category identified by its slug. Provide the slug
        as part of the endpoint URL and the updated category data in the request body.

        ### Path Parameters:
        - `slug`: The unique slug of the category to be updated.

        ### Circular Relationship Check:
        This endpoint performs a circular relationship check during the validation process to prevent the creation
        of circular relationships between categories. (e.g. `A` is the parent of `B` and the user tries to make `B`
        the parent of `A`, this should not be allowed and users should receive 400 Bad request status code.)

        ### Request Body:
        - JSON object representing the updated category.
        - *For more information about requests please check request examples in swagger.*

        ### Responses:
        - 200: The category was successfully updated. Returns the updated category data.
        - 400: Bad request. The request body is invalid, duplicate or missing required fields.
        - 401: Unauthorized. Authentication credentials were not provided or are invalid.
        - 403: Forbidden. The user does not have permission to update the category.
        - 404: Not found. The requested category does not exist.
        - *For more information about responses please check response examples in swagger.*
        """
        return super().update(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: CategorySerializer,
            400: CategorySerializer,
            401: CategorySerializer,
            403: CategorySerializer,
            404: CategorySerializer,
        },
        examples=partial_update_category_examples(),
    )
    def partial_update(self, request, *args, **kwargs):
        """
        ## Partially update an existing category.

        This endpoint allows users to partially update an existing category identified by its slug. Provide the slug
        as part of the endpoint URL and the fields to be updated in the request body.

        ### Path Parameters:
        - `slug`: The unique slug of the category to be updated.

        ### Circular Relationship Check:
        This endpoint performs a circular relationship check during the validation process to prevent the creation
        of circular relationships between categories. (e.g. `A` is the parent of `B` and the user tries to make `B`
        the parent of `A`, this should not be allowed and users should receive 400 Bad request status code.)

        ### Request Body:
        - Provide the fields to be updated in the request body. Only the specified fields will be updated.
        - *For more information about requests please check request examples in swagger.*

        ### Responses:
        - 200: The category was successfully partially updated. Returns the updated category data.
        - 400: Bad request. The request body is invalid, duplicate or missing required fields.
        - 401: Unauthorized. Authentication credentials were not provided or are invalid.
        - 403: Forbidden. The user does not have permission to partially update the category.
        - 404: Not found. The requested category does not exist.
        - *For more information about responses please check response examples in swagger.*
        """
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        responses={
            204: None,
            401: CategorySerializer,
            403: CategorySerializer,
            404: CategorySerializer,
        },
        examples=delete_category_examples(),
    )
    def destroy(self, request, *args, **kwargs):
        """
        ## Delete an existing category.

        This endpoint allows users to delete an existing category identified by its slug.

        ### Path Parameters:
        - `slug`: The unique slug of the category to be deleted.

        ### Responses:
        - 204: The category was successfully deleted. No content in the response body.
        - 401: Unauthorized. Authentication credentials were not provided or are invalid.
        - 403: Forbidden. The user does not have permission to delete the category.
        - 404: Not found. The requested category does not exist.
        - *For more information about responses please check response examples in swagger.*
        """
        return super().destroy(request, *args, **kwargs)
