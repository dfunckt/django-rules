from django.test import TestCase
from django.urls import reverse

from . import TestData


class ModelAdminTests(TestData, TestCase):
    def test_change_book(self):
        # adrian can change his book as its author
        self.assertTrue(self.client.login(username='adrian', password='secr3t'))
        response = self.client.get(reverse('admin:testapp_book_change', args=(1,)))
        self.assertEqual(response.status_code, 200)

        # martin can change adrian's book as an editor
        self.assertTrue(self.client.login(username='martin', password='secr3t'))
        response = self.client.get(reverse('admin:testapp_book_change', args=(1,)))
        self.assertEqual(response.status_code, 200)

    def test_delete_book(self):
        # martin can *not* delete adrian's book
        self.assertTrue(self.client.login(username='martin', password='secr3t'))
        response = self.client.get(reverse('admin:testapp_book_delete', args=(1,)))
        self.assertEqual(response.status_code, 403)

        # adrian can delete his book as its author
        self.assertTrue(self.client.login(username='adrian', password='secr3t'))
        response = self.client.get(reverse('admin:testapp_book_delete', args=(1,)))
        self.assertEqual(response.status_code, 200)
