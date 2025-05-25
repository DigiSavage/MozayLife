"""
tests.py

PURPOSE:
    Contains basic unit tests for your Django app.

DETAILS:
    - This sample test ensures your test framework is set up and working.
    - Add more tests to cover your views, forms, models, and utility functions.

HOW TO RUN:
    python manage.py test

MODERNIZATION NOTES:
    - Compatible with Django 3+ and Python 3.
    - Use Django's TestCase class for all new test classes.

"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """Tests that 1 + 1 always equals 2."""
        self.assertEqual(1 + 1, 2)