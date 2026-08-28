"""API routes for the assets app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import  CollectionViewSet, TagViewSet

router = DefaultRouter()

router.register(r"tags", TagViewSet, basename="tag")
router.register(r"collections", CollectionViewSet, basename="collection")

urlpatterns = [
    path("", include(router.urls)),
]