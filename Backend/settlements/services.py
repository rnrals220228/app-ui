from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from trips.models import TripParticipant
from .models import PaymentChannel, Receipt, Settlement, SettlementProof


def _validate_trip_leader(*, trip, user):
    if trip.leader_user_id != user.id:
        raise PermissionDenied("방장만 수행할 수 있습니다.")


def _validate_trip_participant(*, trip, user):
    exists = TripParticipant.objects.filter(
        trip=trip,
        user=user,
        status="JOINED",
    ).exists()
    if not exists:
        raise PermissionDenied("현재 참가 중인 사용자만 수행할 수 있습니다.")


@transaction.atomic
def upsert_payment_channel(*, trip, user, validated_data):
    _validate_trip_leader(trip=trip, user=user)

    channel, _ = PaymentChannel.objects.update_or_create(
        trip=trip,
        defaults={
            "provider": validated_data["provider"],
            "payment_link": validated_data["payment_link"],
            "account_holder_name": validated_data.get("account_holder_name"),
            "updated_by": user,
        },
    )
    return channel


@transaction.atomic
def create_receipt(*, trip, user, validated_data):
    _validate_trip_leader(trip=trip, user=user)

    if hasattr(trip, "receipt"):
        raise ValidationError("이미 영수증이 등록된 트립입니다.")

    receipt = Receipt.objects.create(
        trip=trip,
        uploaded_by=user,
        image_url=validated_data["image_url"],
        total_amount=validated_data["total_amount"],
    )
    return receipt


@transaction.atomic
def create_settlements_for_receipt(*, receipt: Receipt, actor):
    trip = receipt.trip
    _validate_trip_leader(trip=trip, user=actor)

    if not hasattr(trip, "payment_channel"):
        raise ValidationError("먼저 결제 링크를 등록해야 합니다.")

    participants = list(
        TripParticipant.objects.filter(
            trip=trip,
            status="JOINED",
        ).select_related("user")
    )

    if len(participants) < 2:
        raise ValidationError("정산하려면 최소 2명 이상의 참가자가 필요합니다.")

    payee_user = receipt.uploaded_by
    participant_user_ids = {p.user_id for p in participants}

    if payee_user.id not in participant_user_ids:
        raise ValidationError("영수증 업로더는 현재 참가자여야 합니다.")

    if receipt.settlements.exists():
        raise ValidationError("이미 정산이 생성된 영수증입니다.")

    headcount = len(participants)
    base_amount = receipt.total_amount // headcount
    remainder = receipt.total_amount % headcount

    created = []
    for participant in participants:
        if participant.user_id == payee_user.id:
            continue

        share_amount = base_amount
        if remainder > 0:
            share_amount += 1
            remainder -= 1

        settlement = Settlement.objects.create(
            receipt=receipt,
            payer_user=participant.user,
            payee_user=payee_user,
            share_amount=share_amount,
            status="REQUESTED",
        )
        created.append(settlement)

    return created


@transaction.atomic
def mark_settlement_paid_self(*, settlement: Settlement, user):
    if settlement.payer_user_id != user.id:
        raise PermissionDenied("본인 정산만 송금 완료 처리할 수 있습니다.")

    if settlement.status != "REQUESTED":
        raise ValidationError("현재 송금 완료 처리할 수 없는 상태입니다.")

    settlement.status = "PAID_SELF"
    settlement.paid_self_at = timezone.now()
    settlement.save(update_fields=["status", "paid_self_at"])
    return settlement


@transaction.atomic
def upload_settlement_proof(*, settlement: Settlement, user, image_url: str):
    if settlement.payer_user_id != user.id:
        raise PermissionDenied("본인 정산에만 증빙을 업로드할 수 있습니다.")

    if settlement.status not in ["REQUESTED", "PAID_SELF", "DISPUTED"]:
        raise ValidationError("현재 증빙을 업로드할 수 없는 상태입니다.")

    proof = SettlementProof.objects.create(
        settlement=settlement,
        uploaded_by=user,
        image_url=image_url,
    )
    return proof


@transaction.atomic
def confirm_settlement(*, settlement: Settlement, user):
    if settlement.payee_user_id != user.id:
        raise PermissionDenied("수취인만 정산을 확인할 수 있습니다.")

    if settlement.status != "PAID_SELF":
        raise ValidationError("먼저 상대방이 송금 완료 처리를 해야 합니다.")

    has_proof = settlement.proofs.exists()

    settlement.status = "CONFIRMED"
    settlement.confirmed_at = timezone.now()
    settlement.verified_by = user
    settlement.verification_method = "PROOF_IMAGE" if has_proof else "MANUAL"
    settlement.save(
        update_fields=[
            "status",
            "confirmed_at",
            "verified_by",
            "verification_method",
        ]
    )
    return settlement


@transaction.atomic
def dispute_settlement(*, settlement: Settlement, user):
    if user.id not in [settlement.payer_user_id, settlement.payee_user_id]:
        raise PermissionDenied("정산 당사자만 이의제기할 수 있습니다.")

    if settlement.status not in ["REQUESTED", "PAID_SELF"]:
        raise ValidationError("현재 이의제기할 수 없는 상태입니다.")

    settlement.status = "DISPUTED"
    settlement.save(update_fields=["status"])
    return settlement