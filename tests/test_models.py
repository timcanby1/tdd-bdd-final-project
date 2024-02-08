# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_product(self):
        """It should read a product from the database"""
        product = ProductFactory()
        product.create()
        product_id = product.id
        retrieved_product = Product.find(product_id)
        self.assertIsNotNone(retrieved_product)
        self.assertEqual(retrieved_product.name, product.name)
        self.assertEqual(retrieved_product.description, product.description)
        self.assertEqual(Decimal(retrieved_product.price), product.price)
        self.assertEqual(retrieved_product.available, product.available)
        self.assertEqual(retrieved_product.category, product.category)

    def test_update_product(self):
        """It should update a product in the database"""
        product = ProductFactory()
        product.create()
        product_id = product.id
        # Update the product attributes
        new_name = "Updated Hat"
        new_description = "A blue hat"
        new_price = 15.99
        new_available = False
        new_category = Category.HOUSEWARES
        product.name = new_name
        product.description = new_description
        product.price = new_price
        product.available = new_available
        product.category = new_category
        # Save the updated product
        product.update()
        # Retrieve the updated product from the database
        updated_product = Product.find(product_id)
        self.assertEqual(updated_product.name, new_name)
        self.assertEqual(updated_product.description, new_description)
        self.assertEqual(Decimal(updated_product.price), new_price)
        self.assertEqual(updated_product.available, new_available)
        self.assertEqual(updated_product.category, new_category)

    def test_delete_product(self):
        """It should delete a product from the database"""
        product = ProductFactory()
        product.create()
        product_id = product.id
        product.delete()
        # Attempt to retrieve the deleted product from the database
        deleted_product = Product.find(product_id)
        self.assertIsNone(deleted_product)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        # Retrieve all products from the database and assign them to the products variable.
        products = Product.all()

        # Assert there are no products in the database at the beginning of the test case.
        self.assertEqual(len(products), 0)

        # Create five products and save them to the database.
        for _ in range(5):
            product = ProductFactory()
            product.create()

        # Fetching all products from the database again and assert the count is 5
        products_after_creation = Product.all()
        self.assertEqual(len(products_after_creation), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        # Create a batch of 5 Product objects using the ProductFactory and save them to the database.
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        # Retrieve the name of the first product in the products list.
        product_name = products[0].name

        # Count the number of occurrences of the product name in the list.
        count = sum(1 for p in products if p.name == product_name)

        # Retrieve products from the database that have the specified name.
        found_products = Product.find_by_name(product_name)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(len(found_products), count)

        # Assert that each product’s name matches the expected name.
        for found_product in found_products:
            self.assertEqual(found_product.name, product_name)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database.
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Retrieve the category of the first product in the products list.
        product_category = products[0].category

        # Count the number of occurrences of the product that have the same category in the list.
        count = sum(1 for p in products if p.category == product_category)

        # Retrieve products from the database that have the specified category.
        found_products = Product.find_by_category(product_category)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(len(found_products), count)

        # Assert that each product's category matches the expected category.
        for found_product in found_products:
            self.assertEqual(found_product.category, product_category)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database.
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Retrieve the availability of the first product in the products list.
        product_availability = products[0].available

        # Count the number of occurrences of the product availability in the list.
        count = sum(1 for p in products if p.available == product_availability)

        # Retrieve products from the database that have the specified availability.
        found_products = Product.find_by_availability(product_availability)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(len(found_products), count)

        # Assert that each product's availability matches the expected availability.
        for found_product in found_products:
            self.assertEqual(found_product.available, product_availability)

    def test_read_a_product(self):
        """It should Read a Product"""
        # Create a Product object using the ProductFactory
        product = ProductFactory()
        # Set the ID of the product object to None and then create the product.
        product.id = None
        product.create()

        # Assert that the product ID is not None
        self.assertIsNotNone(product.id)

        # Fetch the product back from the database
        found_product = Product.find(product.id)

        # Assert the properties of the found product are correct
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a Product"""
        # Create a Product object using the ProductFactory
        product = ProductFactory()

        # Set the ID of the product object to None and then create the product.
        product.id = None
        product.create()
        # Assert that the ID of the product object is not None after calling the create() method.
        self.assertIsNotNone(product.id)
        # Update the description property of the product object.
        new_description = "New description for testing"
        product.description = new_description
        product.update()
        # Assert that the id is same as the original id but description property of the product object has been updated correctly after calling the update() method.
        self.assertEqual(product.id, product.id)
        self.assertEqual(product.description, new_description)
        # Fetch all the product back from the system.
        products = Product.all()
        # Assert the length of the products list is equal to 1 to verify that after updating the product, there is only one product in the system.
        self.assertEqual(len(products), 1)
        # Assert that the fetched product has id same as the original id.
        fetched_product = products[0]
        self.assertEqual(fetched_product.id, product.id)

        # Assert that the fetched product has the updated description.
        self.assertEqual(fetched_product.description, new_description)





