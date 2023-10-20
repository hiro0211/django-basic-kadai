from django.contrib import admin 
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import PhotoListView, PhotoDetailView, TagPhotoListView

urlpatterns = [
  path("", PhotoListView.as_view(), name="photo-list"),
  path("photo/<int:pk>", PhotoDetailView.as_view(), name="photo-detail"),
  path("photo/<int:pk>", TagPhotoListView.as_view(), name="tag-photo-list"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)