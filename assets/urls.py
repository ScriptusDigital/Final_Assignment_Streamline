"""API routes for the assets app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import  CollectionViewSet, TagViewSet, AssetViewSet

router = DefaultRouter()

router.register(r"tags", TagViewSet, basename="tag")
router.register(r"collections", CollectionViewSet, basename="collection")
router.register(r"assets", AssetViewSet, basename="asset")

urlpatterns = [
    path("", include(router.urls)),
]