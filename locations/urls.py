from django.urls import path, include
from rest_framework.routers import DefaultRouter
from locations.views import CityViewSet, CountryViewSet

router = DefaultRouter()
router.register('city', CityViewSet)
router.register('country', CountryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]