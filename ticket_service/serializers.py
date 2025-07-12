from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ticket_service.models import AirplaneType, Airplane, Airport, Route, Crew, Flight, Ticket, Order
from user.serializers import UserSerializer, UserListSerializer


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "name"]

class AirplaneTypeDetailSerializer(AirplaneTypeSerializer):
    class Meta:
        model = AirplaneType
        fields = ["name"]


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "image"]


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeDetailSerializer(many=False, read_only=True)
    airplane_type_id = serializers.PrimaryKeyRelatedField(
        queryset=AirplaneType.objects.all(),
        write_only=True,
    )
    class Meta:
        model = Airplane
        fields = ["id", "name", "airplane_type", "airplane_type_id", "rows", "seats_on_row", "capacity"]

    def create(self, validated_data):
        airplane_type = validated_data.pop("airplane_type_id")
        return Airplane.objects.create(airplane_type=airplane_type, **validated_data)


class AirportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city"]

class AirportListSerializer(AirportDetailSerializer):
    class Meta:
        model = Airport
        fields = ["name"]


class RouteDetailSerializer(serializers.ModelSerializer):
    source = AirportListSerializer(read_only=True)
    destination = AirportListSerializer(read_only=True)
    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]

class RouteListSerializer(RouteDetailSerializer):
    source = AirportListSerializer(read_only=True)
    destination = AirportListSerializer(read_only=True)
    class Meta:
        model = Route
        fields = ["source", "destination"]


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "full_name"]

    @staticmethod
    def get_full_name(obj):
        return f"{obj.first_name} {obj.last_name}"


class CrewDetailSerializer(CrewSerializer):
    class Meta:
        model = Crew
        fields = ["full_name"]


class FlightSerializer(serializers.ModelSerializer):
    crew = CrewDetailSerializer(many=True, read_only=True)
    crew_id = serializers.PrimaryKeyRelatedField(queryset=Crew.objects.all(), many=True, write_only=True)
    class Meta:
        model = Flight
        fields = ["airplane", "route", "departure_time", "arrival_time", "crew", "crew_id"]

    def create(self, validated_data):
        crew = validated_data.pop("crew_id")
        flight = Flight.objects.create(**validated_data)
        flight.crew.set(crew)
        return flight

class FlightListSerializer(FlightSerializer):
    airplane_name =serializers.CharField(source="airplane.name", read_only=True)
    route_source = serializers.CharField(source="route.source", read_only=True)
    route_destination = serializers.CharField(source="route.destination", read_only=True)

    class Meta:
        model = Flight
        fields = ["airplane_name", "route_source", "route_destination", "departure_time", "arrival_time"]


class FlightDetailSerializer(FlightSerializer):
    route_source = serializers.CharField(source="route.source", read_only=True)
    route_destination = serializers.CharField(source="route.destination", read_only=True)
    tickets_available = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Flight
        fields = ("airplane",
                  "route_source",
                  "route_destination",
                  "departure_time",
                  "arrival_time",
                  "tickets_available",
                  "crew",)

    @staticmethod
    def get_tickets_available(self, obj):
        taken_tickets = obj.tickets.count()
        capacity = obj.airplane.capacity
        return capacity - taken_tickets


class TicketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketDetailSerializer(TicketListSerializer):
    flight = FlightListSerializer()
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")

class TicketListCreateSerializer(serializers.ListSerializer):
    def validate(self, data):
        flight = None
        seats = set()
        for item in data:
            row = item["row"]
            seat = item["seat"]
            flight = item["flight"]
            key = (row, seat)

            if key in seats:
                raise serializers.ValidationError(f"Duplicate ticket: row {row}, seat {seat}")
            seats.add(key)

            if Ticket.objects.filter(row=row, seat=seat, flight=flight).exists():
                raise serializers.ValidationError(f'Ticket already exists: row {row}, seat {seat}')
            Ticket.validate_ticket(row, seat, flight, serializers.ValidationError)

        return data

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        order, _ = Order.objects.get_or_create(user=user)

        tickets = [Ticket(order=order, **item) for item in validated_data]
        return Ticket.objects.bulk_create(tickets)


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")
        list_serializer_class = TicketListCreateSerializer

    def validate(self, attrs):

        airplane = attrs["flight"].airplane
        if attrs["row"] > airplane.rows:
            raise serializers.ValidationError("Choose a valid row")
        if attrs["seat"] > airplane.seats_on_row:
            raise serializers.ValidationError("Choose a valid seat")

        Ticket.validate_ticket(
            row=attrs["row"],
            seat=attrs["seat"],
            flight=attrs["flight"],
            error_to_raise=serializers.ValidationError
        )
        Ticket.validate_ticket(attrs["row"], attrs["seat"], attrs["flight"], serializers.ValidationError)
        if Ticket.objects.filter(row=attrs["row"], seat=attrs["seat"], flight=attrs["flight"]).exists():
            raise ValidationError("Ticket already exists")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        order, _ = Order.objects.get_or_create(user=user)

        ticket = Ticket.objects.create(
            order=order,
            **validated_data,
        )
        return ticket


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True)
    class Meta:
        model = Order
        fields = ("id", "tickets", "user", "created_at")

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data, user=user)
        for ticket_data in tickets_data:
            Ticket.objects.create(
                user=user,
                order=order,
                **ticket_data
            )

        return order

class OrderListSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    class Meta:
        model = Order
        fields = ("id", "user", "created_at")

    @staticmethod
    def get_user(obj):
        return obj.user

class OrderDetailSerializer(serializers.ModelSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Order
        fields = ("id", "tickets", "user", "created_at")
