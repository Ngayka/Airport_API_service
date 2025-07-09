from django.urls import path, include
from rest_framework import routers

from ticket_service.models import AirplaneType, Airplane
from ticket_service.views import FlightList, CrewList

app_name = 'ticket_service'

router = routers.DefaultRouter()
router.register("flights", FlightList, basename="flights")
router.register("crew", CrewList, basename="crew")
router.register("airplane_type", AirplaneType, basename="airplane_type")
router.register("airplane", Airplane, basename="airplane")

urlpatterns = [path("", include(router.urls))]