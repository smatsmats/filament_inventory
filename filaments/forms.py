from django import forms

from .models import Filament


class FilamentForm(forms.ModelForm):
    class Meta:
        model = Filament
        exclude = ["price_per_gram"]
        widgets = {
            "bought": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "used_up": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class CsvImportForm(forms.Form):
    file = forms.FileField(label="CSV file")
