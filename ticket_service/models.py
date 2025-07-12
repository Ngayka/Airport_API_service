from django.db import models
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class AirplaneType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name or 'Unnamed type'}"

class Airplane(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    rows = models.IntegerField(null=False, blank=False)
    seats_on_row = models.IntegerField(null=False, blank=False)
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)


    @property
    def capacity(self):
        return self.rows * self.seats_on_row

    def __str__(self):
        return f"{self.name} ({self.airplane_type}, {self.rows}x{self.seats_on_row})"


class Airport(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    closest_big_city = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        if self.closest_big_city:
            return f"{self.name} Airport ({self.closest_big_city})"
        return f"{self.name} Airport"

class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departure")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrival")
    distance = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return f"{self.source.name} → {self.destination.name} ({self.distance} km)"

class Crew(models.Model):
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name

class Flight(models.Model):
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    crew = models.ManyToManyField(Crew)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.route} | {self.departure_time.strftime('%Y-%m-%d %H:%M')}"

class Ticket(models.Model):
    row = models.IntegerField(null=False, blank=False)
    seat = models.IntegerField(null=False, blank=False)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")

    @staticmethod
    def validate_ticket(row, seat, flight, error_to_raise):
        for ticket_attr_value, ticket_attr_name, flight_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_on_row"),
        ]:
            count_attrs = getattr(flight.airplane, flight_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                                          f"number must be in available range: "
                                          f"(1, {flight_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
             )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight,
            ValidationError,
        )

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
        force_insert, force_update, using, update_fields
        )
    def __str__(self):
        return f"Ticket: flight {self.flight}, seat {self.row}{chr(64 + self.seat)}"

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return f"Order #{self.id} by {self.user.email} on {self.created_at.strftime('%Y-%m-%d')}"
