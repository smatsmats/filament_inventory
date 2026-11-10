import csv
import io
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CsvImportForm, FilamentForm
from .models import Filament


def healthz(request):
    return HttpResponse("ok")


@login_required
def filament_list(request):
    qs = Filament.objects.all()
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if q:
        qs = qs.filter(
            Q(brand__icontains=q) | Q(model__icontains=q) | Q(type__icontains=q)
            | Q(color__icontains=q) | Q(store_code__icontains=q)
            | Q(make_code__icontains=q) | Q(nfc__icontains=q) | Q(notes__icontains=q)
        )
    if status == "active":
        qs = qs.filter(used_up__isnull=True)
    elif status == "used":
        qs = qs.filter(used_up__isnull=False)
    return render(request, "filaments/list.html", {"filaments": qs, "q": q, "status": status})


@login_required
def filament_edit(request, pk=None):
    obj = get_object_or_404(Filament, pk=pk) if pk else None
    form = FilamentForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("filament_list")
    return render(request, "filaments/form.html", {"form": form, "obj": obj})


@login_required
def filament_delete(request, pk):
    obj = get_object_or_404(Filament, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("filament_list")
    return render(request, "filaments/confirm_delete.html", {"obj": obj})


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _header_map():
    """Normalized header text (field name or label) -> form field name."""
    m = {}
    for name, field in FilamentForm.base_fields.items():
        m[_norm(name)] = name
        m[_norm(str(field.label or ""))] = name
    m["quantity"] = "quantity_grams"
    m["g"] = "quantity_grams"
    return m


def _clean_value(name, value):
    value = (value or "").strip()
    if name == "price":
        value = value.replace("$", "").replace(",", "")
    elif name == "quantity_grams":
        value = re.sub(r"\s*g(rams?)?$", "", value, flags=re.I).replace(",", "")
    return value


@login_required
def filament_import(request):
    form = CsvImportForm(request.POST or None, request.FILES or None)
    errors = []
    if request.method == "POST" and form.is_valid():
        try:
            text = request.FILES["file"].read().decode("utf-8-sig")
        except UnicodeDecodeError:
            errors.append("File must be UTF-8 encoded text.")
            text = None
        if text is not None:
            reader = csv.DictReader(io.StringIO(text))
            hmap = _header_map()
            cols = {h: hmap[_norm(h)] for h in (reader.fieldnames or []) if _norm(h) in hmap}
            if "brand" not in cols.values():
                errors.append("CSV needs a header row including a Brand column.")
            else:
                forms_ = []
                for line, row in enumerate(reader, start=2):
                    data = {cols[h]: _clean_value(cols[h], row.get(h)) for h in cols}
                    if not any(data.values()):
                        continue
                    if not data.get("quantity_grams"):
                        data.pop("quantity_grams", None)
                        data["quantity_grams"] = 1000
                    f = FilamentForm(data)
                    if f.is_valid():
                        forms_.append(f)
                    else:
                        for field, errs in f.errors.items():
                            errors.append(f"Line {line}, {field}: {' '.join(errs)}")
                if not errors:
                    with transaction.atomic():
                        for f in forms_:
                            f.save()
                    messages.success(request, f"Imported {len(forms_)} roll(s).")
                    return redirect("filament_list")
    return render(request, "filaments/import.html", {"form": form, "errors": errors})
