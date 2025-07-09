from django.urls import path, include
from rest_framework import routers

from ticket_service.views import FlightList, CrewList, AirplaneTypeList, AirplaneList, TicketList, AirportList, \
    RouteList

app_name = 'ticket_service'

router = routers.DefaultRouter()
router.register("flights", FlightList, basename="flights")
router.register("crew", CrewList, basename="crew")
router.register("airplane_types", AirplaneTypeList, basename="airplane_types")
router.register("airplanes", AirplaneList, basename="airplanes")
router.register("airports", AirportList, basename="airports")
router.register("routes", RouteList, basename="routes")
router.register("tickets", TicketList, basename="tickets")

urlpatterns = [path("", include(router.urls))]