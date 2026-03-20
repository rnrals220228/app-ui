# trips/services.py
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import Trip, TripParticipant
@transaction.atomic
def create_trip(*, user, validated_data):
    trip = Trip.objects.create(
        creator_user=user,
        leader_user=user,
        **validated_data,
    )

    TripParticipant.objects.create(
        trip=trip,
        user=user,
        role="LEADER",
        status="JOINED",
        confirmed_departure=False,
    )

    return trip
@transaction.atomic
def join_trip(*, trip: Trip, user):
    if trip.status != "OPEN":
        raise ValidationError("현재 참가할 수 없는 모집글입니다.")

    existing = TripParticipant.objects.filter(trip=trip, user=user).first()

    if existing:
        if existing.status == "JOINED":
            raise ValidationError("이미 참가한 모집글입니다.")
        else:
            existing.status = "JOINED"
            existing.left_at = None
            existing.save(update_fields=["status", "left_at"])
    else:
        joined_count = trip.trip_participants.filter(status="JOINED").count()
        if joined_count >= trip.capacity:
            raise ValidationError("정원이 가득 찼습니다.")

        TripParticipant.objects.create(
            trip=trip,
            user=user,
            role="MEMBER",
            status="JOINED",
        )

    joined_count = trip.trip_participants.filter(status="JOINED").count()
    if joined_count >= trip.capacity:
        trip.status = "FULL"
        trip.save(update_fields=["status"])

    return trip
@transaction.atomic
def leave_trip(*, trip: Trip, user):
    participant = TripParticipant.objects.filter(
        trip=trip,
        user=user,
        status="JOINED",
    ).first()

    if not participant:
        raise ValidationError("참가 중인 사용자가 아닙니다.")

    if participant.role == "LEADER":
        raise ValidationError("방장은 나갈 수 없습니다. 먼저 방장을 위임하거나 모집을 종료하세요.")

    participant.status = "LEFT"
    participant.left_at = timezone.now()
    participant.save(update_fields=["status", "left_at"])

    joined_count = trip.trip_participants.filter(status="JOINED").count()
    if trip.status == "FULL" and joined_count < trip.capacity:
        trip.status = "OPEN"
        trip.save(update_fields=["status"])

    return trip
@transaction.atomic
def kick_participant(*, trip: Trip, actor, target_user_id: int):
    if trip.leader_user_id != actor.id:
        raise PermissionDenied("방장만 강퇴할 수 있습니다.")

    participant = TripParticipant.objects.filter(
        trip=trip,
        user_id=target_user_id,
        status="JOINED",
    ).first()

    if not participant:
        raise ValidationError("해당 참가자를 찾을 수 없습니다.")

    if participant.role == "LEADER":
        raise ValidationError("방장은 강퇴할 수 없습니다.")

    participant.status = "KICKED"
    participant.left_at = timezone.now()
    participant.save(update_fields=["status", "left_at"])

    joined_count = trip.trip_participants.filter(status="JOINED").count()
    if trip.status == "FULL" and joined_count < trip.capacity:
        trip.status = "OPEN"
        trip.save(update_fields=["status"])

    return trip