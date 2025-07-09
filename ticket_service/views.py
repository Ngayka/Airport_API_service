from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, mixins
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from ticket_service.models import Flight, Crew, AirplaneType, Airplane, Route, Ticket, Airport
from ticket_service.serializers import (FlightSerializer,
                                        FlightListSerializer,
                                        FlightDetailSerializer,
                                        CrewSerializer,
                                        AirplaneTypeSerializer,
                                        AirplaneSerializer,
                                        TicketCreateSerializer,
                                        AirportDetailSerializer,
                                        AirportListSerializer,
                                        RouteListSerializer,
                                        RouteDetailSerializer)


class CrewList(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [IsAdminUser]


class AirplaneTypeList(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminUser]


class AirplaneList(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = [IsAdminUser]


class AirportList(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportDetailSerializer
    permission_classes = [IsAdminUser]

class RouteList(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return RouteDetailSerializer


class FlightList(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Flight.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["airport__id", "departure_time", "route__source__id"]

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        return FlightDetailSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]


class TicketList(mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin,
                 viewsets.GenericViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketCreateSerializer
    permission_classes = [IsAuthenticated]


class TicketAdminList(mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketCreateSerializer
    permission_classes = [IsAdminUser]