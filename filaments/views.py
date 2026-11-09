from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FilamentForm
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
