from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Filament


class FilamentTests(TestCase):
    def test_price_per_gram_computed(self):
        f = Filament.objects.create(brand="Bambu", quantity_grams=1000, price=Decimal("19.99"))
        self.assertEqual(f.price_per_gram, Decimal("0.0200"))

    def test_price_per_gram_blank_without_price(self):
        f = Filament.objects.create(brand="Bambu")
        self.assertIsNone(f.price_per_gram)

    def test_login_required(self):
        r = self.client.get(reverse("filament_list"))
        self.assertEqual(r.status_code, 302)

    def test_add_and_list(self):
        get_user_model().objects.create_user("u", password="p")
        self.client.login(username="u", password="p")
        r = self.client.post(reverse("filament_new"), {
            "brand": "Polymaker", "quantity_grams": 1000, "price": "25.00", "color": "Teal",
        })
        self.assertEqual(r.status_code, 302)
        r = self.client.get(reverse("filament_list"), {"q": "teal"})
        self.assertContains(r, "Polymaker")
        self.assertContains(r, "$0.0250")
