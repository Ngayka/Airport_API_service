from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ticket_service.models import AirplaneType, Airplane, Airport, Route, Crew, Flight


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = "name"


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = "name", "capacity"


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "name", "closest_big_city"


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = "source", "destination", "distance"

class RouteListSerializer(RouteSerializer):
    class Meta:
        model = Route
        fields = "source", "destination"


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = "full_name"


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = "airplane", "route", "departure_time", "arrival_time", "crew",

class FlightListSerializer(FlightSerializer):
    airplane_name =serializers.CharField(source="airplane.name", read_only=True)

    class Meta:
        model = Flight
        fields = "airplane_name", "route", "departure_time", "arrival_time"


class FlightDetailSerializer(FlightSerializer):
    route_source = serializers.CharField(source="route.source", read_only=True)
    route_destination = serializers.CharField(source="route.destination", read_only=True)
    class Meta:
        model = Flight
        fields = ("airplane",
                  "route_source",
                  "route_destination",
                  "departure_time",
                  "arrival_time",
                  "tickets_available",
                  "crew",)

    def get_tickets_available(self, obj):
        taken_tickets = obj.tickets.count()
        capacity = obj.airplane.capacity
        return capacity - taken_tickets

