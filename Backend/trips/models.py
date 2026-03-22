from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Trip(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "OPEN"),
        ("FULL", "FULL"),
        ("CANCELED", "CANCELED"),
        ("CLOSED", "CLOSED"),
        ("COMPLETED", "COMPLETED"   ),
    ]

    creator_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="trips_created",
    )
    leader_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="trips_led",
    )

    depart_name = models.CharField(max_length=80)
    depart_lat = models.DecimalField(max_digits=9, decimal_places=6)
    depart_lng = models.DecimalField(max_digits=9, decimal_places=6)

    arrive_name = models.CharField(max_length=80)
    arrive_lat = models.DecimalField(max_digits=9, decimal_places=6)
    arrive_lng = models.DecimalField(max_digits=9, decimal_places=6)

    depart_time = models.DateTimeField()
    capacity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(4)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    estimated_fare = models.IntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.depart_name} -> {self.arrive_name} ({self.depart_time})"


class TripParticipant(models.Model):
    ROLE_CHOICES = [
        ("LEADER", "LEADER"),
        ("MEMBER", "MEMBER"),
    ]

    STATUS_CHOICES = [
        ("JOINED", "JOINED"),
        ("LEFT", "LEFT"),
        ("KICKED", "KICKED"),
    ]

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="trip_participants",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trip_participants",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="MEMBER")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="JOINED")
    confirmed_departure = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "user"],
                name="unique_trip_participant",
            )
        ]

    def __str__(self):
        return f"{self.trip_id} - {self.user_id}"