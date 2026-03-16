from django.contrib import admin

from .models import Trip, TripParticipant


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "creator_user",
        "leader_user",
        "depart_name",
        "arrive_name",
        "depart_time",
        "capacity",
        "status",
        "estimated_fare",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("depart_name", "arrive_name")


@admin.register(TripParticipant)
class TripParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "trip",
        "user",
        "role",
        "status",
        "seat_position",
        "confirmed_departure",
        "joined_at",
        "left_at",
    )
    list_filter = ("role", "status", "confirmed_departure")
    search_fields = ("trip__depart_name", "user__email", "user__nickname")