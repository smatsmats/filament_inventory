from django.urls import path

from . import views

urlpatterns = [
    path("", views.filament_list, name="filament_list"),
    path("new/", views.filament_edit, name="filament_new"),
    path("import/", views.filament_import, name="filament_import"),
    path("<int:pk>/edit/", views.filament_edit, name="filament_edit"),
    path("<int:pk>/delete/", views.filament_delete, name="filament_delete"),
    path("healthz", views.healthz, name="healthz"),
]
