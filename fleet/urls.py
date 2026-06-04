from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fleet.views import AirportViewSet, AirplaneViewSet, AirplaneSeatViewSet, AirlineViewSet


router = DefaultRouter()
router.register('airports', AirportViewSet)
router.register('airplanes', AirplaneViewSet)
router.register('airplaneseats', AirplaneSeatViewSet)
router.register('airlines', AirlineViewSet)

urlpatterns = [
    path('', include(router.urls)),
]