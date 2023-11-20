from django.contrib import admin 
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
  PhotoListView,
  PhotoDetailView,
  TagPhotoListView,
  PhotoCreateView,
  PhotoUpdateView,
  PhotoDeleteView,
)

urlpatterns = [
  path("", PhotoListView.as_view(), name="photo-list"),
  path("photo/<int:pk>", PhotoDetailView.as_view(), name="photo-detail"),
  path("tag/<str:tag>", TagPhotoListView.as_view(), name="tag-photo-list"),
  path("create/", PhotoCreateView.as_view(), name="photo-create"),
  path("edit/<int:pk>", PhotoUpdateView.as_view(), name="photo-edit"),
  path("delete/<int:pk>", PhotoDeleteView.as_view(), name="photo-delete"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)