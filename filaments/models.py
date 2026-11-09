from decimal import ROUND_HALF_UP, Decimal

from django.db import models


class Filament(models.Model):
    brand = models.CharField(max_length=100)
    store_code = models.CharField(max_length=100, blank=True)
    make_code = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=50, blank=True, help_text="PLA, PETG, ABS, TPU...")
    quantity_grams = models.PositiveIntegerField("Quantity (grams)", default=1000)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    price_per_gram = models.DecimalField(
        "Price / gram", max_digits=10, decimal_places=4, null=True, blank=True, editable=False
    )
    texture = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    nfc = models.CharField("NFC", max_length=100, blank=True)
    source = models.CharField(max_length=100, blank=True)
    bought = models.DateField(null=True, blank=True)
    used_up = models.DateField("Used-up", null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-bought", "-id"]

    def __str__(self):
        return " ".join(p for p in (self.brand, self.model, self.type, self.color) if p)

    def save(self, *args, **kwargs):
        if self.price is not None and self.quantity_grams:
            self.price_per_gram = (self.price / Decimal(self.quantity_grams)).quantize(
                Decimal("0.0001"), rounding=ROUND_HALF_UP
            )
        else:
            self.price_per_gram = None
        super().save(*args, **kwargs)
