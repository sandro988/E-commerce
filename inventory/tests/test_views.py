from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from inventory.models import Category


User = get_user_model()


class BaseCategoryTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="staff_user@email.com",
            password="staff_user_pass",
            is_verified=True,
            is_staff=True,
        )
        cls.token = Token.objects.create(user=cls.user)
        cls.category = Category.objects.create(
            name="Test Category",
            description="Description for Test Category",
        )


class CategoryListTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="staff_user@email.com",
            password="staff_user_pass",
            is_verified=True,
            is_staff=True,
        )

        cls.token = Token.objects.create(user=cls.user)

        # Creating 10 categories
        for i in range(1, 11):
            category_name = f"Category {i}"
            category_description = f"Description for Category {i}"
            Category.objects.create(
                name=category_name,
                description=category_description,
            )

    def setUp(self) -> None:
        self.category_list_url = reverse("category-list")
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_list_categories(self):
        response = self.client.get(self.category_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_list_categories_with_unauthenticated_user(self):
        self.client.credentials()
        response = self.client.get(self.category_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_list_categories_without_permissions(self):
        # Setting is_staff field to false, thus removing necessary permissions
        # for creating, updating and deleting categories from user.
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(self.category_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)


class SubCategoryListTests(BaseCategoryTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        for i in range(1, 11):
            Category.objects.create(
                name=f"Subcategory {i}",
                description=f"Description for Subcategory {i}",
                parent=cls.category,
            )

    def setUp(self):
        self.subcategories_list_url = reverse(
            "category-subcategories-list", kwargs={"slug": self.category.slug}
        )
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_list_subcategories(self):
        response = self.client.get(self.subcategories_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_list_subcategories_with_unauthenticated_user(self):
        self.client.credentials()
        response = self.client.get(self.subcategories_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_list_subcategories_without_permissions(self):
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(self.subcategories_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_no_subcategories(self):
        Category.objects.create(name="Category with no subcategories")
        new_category = Category.objects.get(name="Category with no subcategories")
        url = reverse("category-subcategories-list", kwargs={"slug": new_category.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_category_not_found(self):
        url = reverse(
            "category-subcategories-list", kwargs={"slug": "non-existent-slug"}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CategoryRetrieveTests(BaseCategoryTestCase):
    def setUp(self):
        self.category_retrieve_url = reverse(
            "category-detail", kwargs={"slug": self.category.slug}
        )
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_retrieve_category(self):
        response = self.client.get(self.category_retrieve_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Category")
        self.assertEqual(response.data["slug"], "test-category")
        self.assertEqual(response.data["description"], "Description for Test Category")
        self.assertEqual(response.data["parent"], None)

    def test_list_categories_with_unauthenticated_user(self):
        self.client.credentials()
        response = self.client.get(self.category_retrieve_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Category")
        self.assertEqual(response.data["slug"], "test-category")

    def test_list_categories_without_permissions(self):
        # Setting is_staff field to false, thus removing necessary permissions
        # for creating, updating and deleting categories from user.
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(self.category_retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Category")
        self.assertEqual(response.data["slug"], "test-category")


class CategoryCreateTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="staff_user@email.com",
            password="staff_user_pass",
            is_verified=True,
            is_staff=True,
        )

        cls.token = Token.objects.create(user=cls.user)

    def setUp(self):
        self.category_create_url = reverse("category-list")
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.category_data = [
            {
                "name": "Mobile Phones",
                "description": "Category for mobile phones",
            },
            {
                "name": "Electronics",
                "description": "Category for Electronics",
            },
        ]
        self.single_category_data = {
            "name": "Pet Food",
            "description": "Category for pet food products",
        }

        self.subcategory_data = {
            "name": "Cat Food",
            "description": "Category for cat food products",
        }

    def test_create_category(self):
        response = self.client.post(
            self.category_create_url,
            self.category_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        categories = Category.objects.all()
        for category in categories:
            self.assertIn(category.name, ["Mobile Phones", "Electronics"])
            self.assertIn(category.slug, ["mobile-phones", "electronics"])
            self.assertIn(
                category.description,
                ["Category for mobile phones", "Category for Electronics"],
            )
            self.assertIsNone(category.parent)

    def test_crete_category_with_just_name(self):
        """
        This test case will test a scenario when user passes only category name to request.
        In this case category should still be created and other fields such as: parent, description, image
        should be set to default value and slug field should be generated from category name.
        """

        self.single_category_data["description"] = None  # Setting description to None.
        response_for_creating_parent_category = self.client.post(
            self.category_create_url,
            self.single_category_data,
            format="json",
        )
        self.assertEqual(
            response_for_creating_parent_category.status_code,
            status.HTTP_201_CREATED,
        )
        new_category = Category.objects.last()
        self.assertIsNotNone(new_category)
        self.assertIsNone(new_category.description)
        self.assertIsNone(new_category.parent)
        self.assertIsNotNone(new_category.slug)
        self.assertEqual(new_category.slug, "pet-food")

    def test_create_subcategory(self):
        # First creating parent category
        response_for_creating_parent_category = self.client.post(
            self.category_create_url,
            self.category_data,
            format="json",
        )
        self.assertEqual(
            response_for_creating_parent_category.status_code,
            status.HTTP_201_CREATED,
        )
        parent_category = Category.objects.last()

        # Creating subcategory
        self.subcategory_data["parent"] = parent_category.id
        response_for_creating_subcategory = self.client.post(
            self.category_create_url,
            self.subcategory_data,
            format="json",
        )
        subcategory = Category.objects.get(name="Cat Food")

        self.assertEqual(
            response_for_creating_subcategory.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(subcategory.parent.id, parent_category.id)
        self.assertEqual(subcategory.name, "Cat Food")
        self.assertEqual(subcategory.slug, "cat-food")
        self.assertEqual(
            subcategory.description,
            "Category for cat food products",
        )

    def test_create_category_with_invalid_parent_id(self):
        invalid_parent_id_data = {
            "name": "Mobile Phones",
            "description": "Category for mobile phones",
            "parent": 9999,  # Invalid parent ID
        }
        response = self.client.post(
            self.category_create_url,
            invalid_parent_id_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), 0)

    def test_create_category_with_invalid_data(self):
        # Creating a category with empty data.
        invalid_data = {}
        response = self.client.post(
            self.category_create_url, invalid_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Creating a category with invalid 'name' field (e.g., too long).
        invalid_data = {
            "name": "a" * 129,  # This exceeds max_length of 128 characters
            "description": "Category description",
        }
        response = self.client.post(
            self.category_create_url,
            invalid_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Creating a category with invalid 'parent' field (e.g., string type instead of primary key).
        invalid_data = {
            "name": "Category Name",  # This exceeds max_length of 128 characters
            "description": "Category description",
            "parent": "String instead of primary key.",
        }
        response = self.client.post(
            self.category_create_url,
            invalid_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Creating a category with invalid 'image' field (e.g., string type instead of file/image).
        invalid_data = {
            "name": "Category Name",  # This exceeds max_length of 128 characters
            "description": "Category description",
            "image": "String instead of file/image.",
        }
        response = self.client.post(
            self.category_create_url,
            invalid_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Ensure that no category was created
        self.assertEqual(Category.objects.count(), 0)

    def test_create_category_with_duplicate_name(self):
        response = self.client.post(
            self.category_create_url, self.single_category_data, format="json"
        )
        response_with_duplicate_data = self.client.post(
            self.category_create_url, self.single_category_data, format="json"
        )

        # Verifying that the API returns a 400 Bad Request status code after second request.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response_with_duplicate_data.status_code, status.HTTP_400_BAD_REQUEST
        )

        # Checking that only one category is created in db.
        self.assertEqual(Category.objects.count(), 1)

    def test_create_subcategory_with_duplicate_name(self):
        # First creating parent category
        response_for_creating_parent_category = self.client.post(
            self.category_create_url,
            self.single_category_data,
            format="json",
        )
        self.assertEqual(
            response_for_creating_parent_category.status_code,
            status.HTTP_201_CREATED,
        )
        parent_category = Category.objects.last()

        # Creating subcategory
        self.subcategory_data["parent"] = parent_category.id
        response_for_creating_subcategory = self.client.post(
            self.category_create_url,
            self.subcategory_data,
            format="json",
        )

        subcategory = Category.objects.get(name="Cat Food")

        self.assertEqual(
            response_for_creating_subcategory.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(subcategory.parent.id, parent_category.id)
        self.assertEqual(subcategory.name, "Cat Food")
        self.assertEqual(subcategory.slug, "cat-food")
        self.assertEqual(
            subcategory.description,
            "Category for cat food products",
        )

        # Creating same subcategory again, but with different description to check that
        # subcategory does not change in any way and no duplicate subcategory is created.
        self.subcategory_data["description"] = "Changed category for cat food products"
        response_for_creating_subcategory = self.client.post(
            self.category_create_url,
            self.subcategory_data,
            format="json",
        )

        self.assertEqual(
            response_for_creating_subcategory.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            Category.objects.get(name="Pet Food").subcategories.all().count(), 1
        )
        subcategory = Category.objects.get(name="Cat Food")
        self.assertNotEqual(
            subcategory.description, "Changed category for cat food products"
        )

    def test_create_subcategory_with_category_data(self):
        """
        This test case tests a scenario when user tries to create a subcategory
        with exactly the same data as the parent category. Parent category can not
        have a subcategory of itself.
        """

        category_response = self.client.post(
            self.category_create_url, self.single_category_data, format="json"
        )
        self.single_category_data["parent"] = Category.objects.last().id
        subcategory_response = self.client.post(
            self.category_create_url, self.single_category_data, format="json"
        )

        self.assertEqual(subcategory_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), 1)
        self.assertIsNone(Category.objects.last().parent)

    def test_create_category_with_unauthenticated_user(self):
        self.client.credentials()  # Removing token

        response = self.client.post(
            self.category_create_url,
            self.category_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Category.objects.count(), 0)

    def test_create_category_without_permissions(self):
        # Setting is_staff field to false, thus removing necessary permissions
        # for creating categories from user.
        self.user.is_staff = False
        self.user.save()

        response = self.client.post(
            self.category_create_url,
            self.category_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Category.objects.count(), 0)

    def test_create_category_with_special_characters_in_name(self):
        special_characters_data = {
            "name": "Category@123",
            "description": "Category with special characters in name",
        }
        response = self.client.post(
            self.category_create_url,
            special_characters_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), 0)

    def test_category_name_case_insensitivity(self):
        # This test checks that category name is case insensitive and we can not
        # have for example these three category names such as: Books, books, BOOKS

        response = self.client.post(
            self.category_create_url,
            self.single_category_data,
            format="json",
        )  # Initial category

        self.single_category_data["name"] = "PET FOOD"
        second_response = self.client.post(
            self.category_create_url,
            self.single_category_data,
            format="json",
        )  # Initial category but in uppercase

        self.single_category_data["name"] = "pet food"
        third_response = self.client.post(
            self.category_create_url,
            self.single_category_data,
            format="json",
        )  # Initial category but in lowercase

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(third_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.last().name, "Pet Food")


class CategoryUpdateTests(BaseCategoryTestCase):
    def setUp(self) -> None:
        self.category_update_url = reverse(
            "category-detail", kwargs={"slug": self.category.slug}
        )
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.updated_data = {
            "name": "Updated Category Name",
            "description": "Updated Description",
        }

    def test_update_with_authenticated_admin_user(self):
        response = self.client.put(
            self.category_update_url, self.updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.updated_data["name"])
        self.assertEqual(response.data["description"], self.updated_data["description"])

    def test_update_with_unauthenticated_user(self):
        self.client.credentials()
        response = self.client.put(
            self.category_update_url, self.updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            str(response.data["detail"]),
            "Authentication credentials were not provided.",
        )
        self.category.refresh_from_db()
        self.assertNotEqual(self.category.name, self.updated_data["name"])
        self.assertNotEqual(self.category.description, self.updated_data["description"])

    def test_update_without_permissions(self):
        self.user.is_staff = False
        self.user.save()
        response = self.client.put(
            self.category_update_url, self.updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            str(response.data["detail"]),
            "You do not have permission to perform this action.",
        )
        self.category.refresh_from_db()
        self.assertNotEqual(self.category.name, self.updated_data["name"])
        self.assertNotEqual(self.category.description, self.updated_data["description"])

    def test_update_with_existing_category(self):
        """
        This test will make sure that if we try to update category with a name of another
        category we get 400 status code and the category is not changed.
        """

        # Creating another category.
        Category.objects.create(name="Existing Category")
        updated_data = {
            "name": "Existing Category",
        }
        # Trying to update the category defined in setUpTestData with the name of an already existing category.
        response = self.client.put(
            self.category_update_url, updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0], "category with this name already exists."
        )
        # Test Category is the category created in setUpTestData
        self.assertIsNotNone(Category.objects.get(name="Test Category"))
        self.assertEqual(Category.objects.all().count(), 2)

    def test_update_names_are_case_insensitive(self):
        data = {"name": "test category"}  # Lowercase variation
        response = self.client.put(self.category_update_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(Category.objects.last().name, "test category")

        data = {"name": "TEST CATEGORY"}  # Uppercase variation
        response = self.client.put(self.category_update_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(Category.objects.last().name, "TEST CATEGORY")

        data = {"name": "TeSt CaTeGoRy"}  # Mixed-case variation
        response = self.client.put(self.category_update_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(Category.objects.last().name, "TeSt CaTeGoRy")

    def test_update_with_very_long_name(self):
        updated_data = {
            "name": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. \
                    Fusce dictum gravida urna, nec malesuada nisi efficitur eget.",
        }  # 'name' has more than 128 characters.
        response = self.client.put(
            self.category_update_url, updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0],
            "Ensure this field has no more than 128 characters.",
        )
        self.assertNotEqual(Category.objects.last().name, updated_data["name"])

    def test_update_name_with_special_characters(self):
        self.updated_data["name"] = "Category !@#$%^&*()"
        response = self.client.put(
            self.category_update_url, self.updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0], "Category name cannot contain special characters."
        )

    def test_update_with_missing_fields(self):
        updated_data = {
            "description": "Updated Description",  # Missing the 'name' field
        }
        response = self.client.put(
            self.category_update_url, updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["name"][0], "This field is required.")
        self.assertNotEqual(
            Category.objects.last().description, updated_data["description"]
        )

    def test_update_with_invalid_image_type(self):
        updated_data = {
            "name": "Category Name",
            "image": "String instead of file/image",
        }
        response = self.client.put(
            self.category_update_url, updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(
            Category.objects.last().image, "String instead of file/image"
        )

    def test_update_with_invalid_parent(self):
        # Updating to a parent that does not exist.
        invalid_parent_id = 999_999_999
        self.updated_data["parent"] = invalid_parent_id
        response = self.client.put(
            self.category_update_url, self.updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["parent"][0],
            f'Invalid pk "{invalid_parent_id}" - object does not exist.',
        )
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent)

        # Passing string in parent field instead of primary key.
        self.updated_data["parent"] = "Not a primary key value"
        response = self.client.put(
            self.category_update_url, self.updated_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["parent"][0],
            "Incorrect type. Expected pk value, received str.",
        )
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent)

    def test_update_with_null_parent(self):
        # First creating second category
        new_category = Category.objects.create(
            name="Second test category",
            description="Description for second test category",
            parent=self.category,
        )
        category_update_url = reverse(
            "category-detail", kwargs={"slug": new_category.slug}
        )
        # Setting parent to None, which means that this category now should have no parent
        update_data = {
            "name": "Second test category",
            "description": "Description for second test category",
            "parent": None,
        }
        response = self.client.put(category_update_url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(Category.objects.get(name="Second test category").parent)

    def test_update_parent_with_itself(self):
        data = {
            "name": self.category.name,
            "parent": self.category.id,  # Passing id of itself.
        }

        response = self.client.put(self.category_update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("A category cannot be its own parent.", str(response.data))
        # Checking that the category's parent relationship remains unchanged
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent)

    def test_update_with_circular_relationship(self):
        # First testing with only one subcategory
        second_category = Category.objects.create(
            name="Second Category", parent=self.category
        )
        data = {
            "name": self.category.name,
            # Attempting to make second category its own parent (circular relationship).
            "parent": second_category.id,
        }
        response = self.client.put(self.category_update_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This change would create a circular relationship.", str(response.data)
        )
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent)

        # Testing with a scenario where the category has a subcategory and the subcategory
        # has the subcategory of its own. (e.g. A --> B --> C).

        third_category = Category.objects.create(
            # Making second category parent of third category. Thus we will have relationship
            # like this: (self.category --> second_category --> third_category)
            name="Third Category",
            parent=second_category,
        )
        data = {
            "name": self.category.name,
            # Making third category a parent of first category which in turn is the parent
            # of second category(Circular relationship).
            "parent": third_category.id,
        }

        response = self.client.put(self.category_update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This change would create a circular relationship.", str(response.data)
        )
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent)

        # Testing for circular relationship with subcategory and its own subcategory.
        # (e.g. A --> B --> C, and user tries to make C parent of B.)

        data = {"name": second_category.name, "parent": third_category.id}
        category_update_url = reverse(
            "category-detail", kwargs={"slug": second_category.slug}
        )
        response = self.client.put(category_update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This change would create a circular relationship.", str(response.data)
        )
        self.category.refresh_from_db()
        self.assertNotEqual(second_category.parent, third_category)
        self.assertEqual(second_category.parent, self.category)


class CategoryPartialUpdateTests(BaseCategoryTestCase):
    def setUp(self) -> None:
        self.category_partial_update_url = reverse(
            "category-detail", kwargs={"slug": self.category.slug}
        )
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.partial_update_data = {
            "description": "Updated Description",
        }

    def test_partial_update_authenticated_admin_user(self):
        response = self.client.patch(
            self.category_partial_update_url,
            self.partial_update_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["description"], self.partial_update_data["description"]
        )
        # Name or any other field should stay the same
        self.assertEqual(response.data["name"], self.category.name)

    def test_partial_update_unauthenticated_user(self):
        self.client.credentials()
        response = self.client.patch(
            self.category_partial_update_url,
            self.partial_update_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_without_permissions(self):
        self.user.is_staff = False
        self.user.save()
        response = self.client.patch(
            self.category_partial_update_url, self.partial_update_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_with_existing_category(self):
        """
        This test will make sure that if we try to update category with a name of another
        category we get 400 status code and the category is not changed.
        """

        # Creating another category.
        Category.objects.create(name="Existing Category")
        updated_data = {
            "name": "Existing Category",
        }
        # Trying to update the category defined in setUpTestData with the name of an already existing category.
        response = self.client.patch(
            self.category_partial_update_url, updated_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0], "category with this name already exists."
        )
        # Test Category is the category created in setUpTestData
        self.assertIsNotNone(Category.objects.get(name="Test Category"))
        self.assertEqual(Category.objects.all().count(), 2)

    def test_partial_update_names_are_case_insensitive(self):
        data = {"name": "test category"}  # Lowercase variation
        response = self.client.patch(
            self.category_partial_update_url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(Category.objects.last().name, "test category")

        data = {"name": "TEST CATEGORY"}  # Uppercase variation
        response = self.client.patch(
            self.category_partial_update_url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(Category.objects.last().name, "TEST CATEGORY")

        data = {"name": "TeSt CaTeGoRy"}  # Mixed-case variation
        response = self.client.patch(
            self.category_partial_update_url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(Category.objects.last().name, "TeSt CaTeGoRy")

    def test_update_with_very_long_name(self):
        updated_data = {
            "name": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. \
                    Fusce dictum gravida urna, nec malesuada nisi efficitur eget.",
        }  # 'name' has more than 128 characters.
        response = self.client.patch(
            self.category_partial_update_url,
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0],
            "Ensure this field has no more than 128 characters.",
        )
        self.assertNotEqual(Category.objects.last().name, updated_data["name"])

    def test_update_name_with_special_characters(self):
        self.partial_update_data["name"] = "Category !@#$%^&*()"
        response = self.client.patch(
            self.category_partial_update_url,
            self.partial_update_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0], "Category name cannot contain special characters."
        )

    def test_update_with_invalid_image_type(self):
        updated_data = {
            "image": "String instead of file/image",
        }
        response = self.client.patch(
            self.category_partial_update_url,
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(
            Category.objects.last().image, "String instead of file/image"
        )

    def test_update_with_invalid_parent(self):
        # Updating to a parent that does not exist.
        invalid_parent_id = 999_999_999
        self.partial_update_data["parent"] = invalid_parent_id
        response = self.client.patch(
            self.category_partial_update_url, self.partial_update_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["parent"][0],
            f'Invalid pk "{invalid_parent_id}" - object does not exist.',
        )
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent)

        # Passing string in parent field instead of primary key.
        self.partial_update_data["parent"] = "Not a primary key value"
        response = self.client.patch(
            self.category_partial_update_url, self.partial_update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["parent"][0],
            "Incorrect type. Expected pk value, received str.",
        )
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent)

    def test_update_with_null_parent(self):
        # First creating second category
        new_category = Category.objects.create(
            name="Second test category",
            description="Description for second test category",
            parent=self.category,
        )
        category_partial_update_url = reverse(
            "category-detail", kwargs={"slug": new_category.slug}
        )
        update_data = {"parent": None}
        response = self.client.patch(
            category_partial_update_url,
            update_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(Category.objects.get(name="Second test category").parent)

    def test_update_parent_with_itself(self):
        data = {
            "parent": self.category.id,  # Passing id of itself.
        }
        response = self.client.patch(
            self.category_partial_update_url,
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("A category cannot be its own parent.", str(response.data))
        # Checking that the category's parent relationship remains unchanged
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent)

    def test_update_with_circular_relationship(self):
        # First testing with only one subcategory
        second_category = Category.objects.create(
            name="Second Category", parent=self.category
        )
        data = {
            # Attempting to make second category its own parent (circular relationship).
            "parent": second_category.id,
        }
        response = self.client.patch(
            self.category_partial_update_url, data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This change would create a circular relationship.", str(response.data)
        )
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent)

        # Testing with a scenario where the category has a subcategory and the subcategory
        # has the subcategory of its own. (e.g. A --> B --> C).

        third_category = Category.objects.create(
            # Making second category parent of third category. Thus we will have relationship
            # like this: (self.category --> second_category --> third_category)
            name="Third Category",
            parent=second_category,
        )
        data = {
            "name": self.category.name,
            # Making third category a parent of first category which in turn is the parent
            # of second category(Circular relationship).
            "parent": third_category.id,
        }

        response = self.client.patch(
            self.category_partial_update_url, data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This change would create a circular relationship.", str(response.data)
        )
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent)

        # Testing for circular relationship with subcategory and its own subcategory.
        # (e.g. A --> B --> C, and user tries to make C parent of B.)

        data = {"name": second_category.name, "parent": third_category.id}
        category_partial_update_url = reverse(
            "category-detail", kwargs={"slug": second_category.slug}
        )
        response = self.client.patch(category_partial_update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "This change would create a circular relationship.", str(response.data)
        )
        self.category.refresh_from_db()
        self.assertNotEqual(second_category.parent, third_category)
        self.assertEqual(second_category.parent, self.category)


class CategoryDeleteTests(BaseCategoryTestCase):
    def setUp(self) -> None:
        self.category_delete_url = reverse(
            "category-detail", kwargs={"slug": self.category.slug}
        )
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_delete_authenticated_admin_user(self):
        response = self.client.delete(self.category_delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.all().count(), 0)

    def test_delete_unauthenticated_user(self):
        self.client.credentials()
        response = self.client.delete(self.category_delete_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Category.objects.all().count(), 1)

    def test_delete_without_permissions(self):
        self.user.is_staff = False
        self.user.save()

        response = self.client.delete(self.category_delete_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_non_existing_category(self):
        self.category_delete_url = reverse(
            "category-detail", kwargs={"slug": "non-existing-slug"}
        )
        response = self.client.delete(self.category_delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
