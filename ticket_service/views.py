from rest_framework import viewsets
from rest_framework.generics import mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ticket_service.models import Flight, Crew, AirplaneType, Airplane, Route, Ticket, Airport, Order
from ticket_service.serializers import (FlightSerializer,
                                        FlightListSerializer,
                                        FlightDetailSerializer,
                                        CrewSerializer,
                                        AirplaneTypeSerializer,
                                        AirplaneSerializer,
                                        TicketCreateSerializer,
                                        AirportDetailSerializer,
                                        RouteListSerializer,
                                        RouteDetailSerializer,
                                        TicketListSerializer,
                                        TicketDetailSerializer,
                                        OrderListSerializer,
                                        OrderCreateSerializer,
                                        OrderDetailSerializer)


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


class FlightSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 20


class FlightList(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    queryset = Flight.objects.all()
    pagination_class = FlightSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["route__destination", "departure_time", "route__source"]

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "create":
            return FlightSerializer
        return FlightDetailSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()


class TicketList(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):

    queryset = Ticket.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["flight",]
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            queryset = Ticket.objects.all()
        elif user.is_authenticated:
            queryset = Ticket.objects.filter(user=user)
        else:
            queryset = Ticket.objects.none()
        if self.action == 'list':
            return queryset.prefetch_related("flight__airplane")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["list"]:
            return TicketListSerializer
        if self.action == "create":
            return TicketCreateSerializer
        return TicketDetailSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [IsAuthenticated()]
        if self.action in ["partial_update", "destroy", "update"]:
            return [IsAdminUser()]
        return super().get_permissions()


class OrderViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            queryset = Order.objects.all()
        elif user.is_authenticated:
            queryset = Order.objects.filter(user=user)
        else:
            queryset = Order.objects.none()
        if self.action == 'list':
            return queryset.prefetch_related("tickets__user")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["list"]:
            return OrderListSerializer
        if self.action == "create":
            return OrderCreateSerializer
        return OrderDetailSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()
