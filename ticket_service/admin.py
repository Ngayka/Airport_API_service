from django.contrib import admin

from ticket_service.models import Ticket, Order, AirplaneType, Airplane, Route, Flight, Crew, Airport


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInline]

admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Ticket)
admin.site.register(Route)
admin.site.register(Crew)
admin.site.register(Flight)
