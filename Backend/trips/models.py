from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class Trip(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "OPEN"),
        ("FULL", "FULL"),
        ("CANCELED", "CANCELED"),
        ("CLOSED", "CLOSED"),
        ("COMPLETED", "COMPLETED"),
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
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(capacity__gte=2) & Q(capacity__lte=4),
                name="trips_trip_capacity_range",
            ),
            models.CheckConstraint(
                condition=Q(estimated_fare__isnull=True) | Q(estimated_fare__gte=0),
                name="trips_trip_estimated_fare_nonnegative_or_null",
            ),
            models.CheckConstraint(
                condition=Q(depart_lat__gte=-90) & Q(depart_lat__lte=90),
                name="trips_trip_depart_lat_range",
            ),
            models.CheckConstraint(
                condition=Q(depart_lng__gte=-180) & Q(depart_lng__lte=180),
                name="trips_trip_depart_lng_range",
            ),
            models.CheckConstraint(
                condition=Q(arrive_lat__gte=-90) & Q(arrive_lat__lte=90),
                name="trips_trip_arrive_lat_range",
            ),
            models.CheckConstraint(
                condition=Q(arrive_lng__gte=-180) & Q(arrive_lng__lte=180),
                name="trips_trip_arrive_lng_range",
            ),
        ]
    

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
    
    SEAT_POSITION_CHOICES = [
        ("FRONT_PASSENGER", "FRONT_PASSENGER"),
        ("REAR_LEFT", "REAR_LEFT"), 
        ("REAR_RIGHT", "REAR_RIGHT"),   
        ("REAR_MIDDLE", "REAR_MIDDLE"),
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
    seat_position = models.CharField(max_length=20, choices=SEAT_POSITION_CHOICES,)
    confirmed_departure = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "user"],
                name="unique_trip_participant",
            ),
            models.UniqueConstraint(
                fields=["trip", "seat_position"],
                name="unique_trip_seat_position",
            ),
        ]

    def __str__(self):
        return f"{self.trip_id} - {self.user_id}"