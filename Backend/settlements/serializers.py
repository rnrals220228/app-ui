from rest_framework import serializers

from .models import PaymentChannel, Receipt, Settlement, SettlementProof


class PaymentChannelSerializer(serializers.ModelSerializer):
    trip_id = serializers.IntegerField(source="trip.id", read_only=True)

    class Meta:
        model = PaymentChannel
        fields = [
            "id",
            "trip_id",
            "provider",
            "payment_link",
            "account_holder_name",
            "updated_by",
            "updated_at",
        ]
        read_only_fields = ["id", "trip_id", "updated_by", "updated_at"]


class PaymentChannelUpsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentChannel
        fields = [
            "provider",
            "payment_link",
            "account_holder_name",
        ]


class ReceiptSerializer(serializers.ModelSerializer):
    trip_id = serializers.IntegerField(source="trip.id", read_only=True)
    uploaded_by_id = serializers.IntegerField(source="uploaded_by.id", read_only=True)

    class Meta:
        model = Receipt
        fields = [
            "id",
            "trip_id",
            "uploaded_by_id",
            "image_url",
            "total_amount",
            "status",
            "confirmed_at",
            "created_at",
        ]
        read_only_fields = ["id", "trip_id", "uploaded_by_id", "status", "confirmed_at", "created_at"]


class ReceiptCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = [
            "image_url",
            "total_amount",
        ]


class SettlementProofSerializer(serializers.ModelSerializer):
    uploaded_by_id = serializers.IntegerField(source="uploaded_by.id", read_only=True)

    class Meta:
        model = SettlementProof
        fields = [
            "id",
            "uploaded_by_id",
            "image_url",
            "created_at",
        ]
        read_only_fields = ["id", "uploaded_by_id", "created_at"]


class SettlementSerializer(serializers.ModelSerializer):
    trip_id = serializers.IntegerField(source="receipt.trip.id", read_only=True)
    receipt_id = serializers.IntegerField(source="receipt.id", read_only=True)
    payer_user_id = serializers.IntegerField(source="payer_user.id", read_only=True)
    payee_user_id = serializers.IntegerField(source="payee_user.id", read_only=True)
    verified_by_id = serializers.IntegerField(source="verified_by.id", read_only=True)
    proofs = SettlementProofSerializer(many=True, read_only=True)
    payment_channel = serializers.SerializerMethodField()

    class Meta:
        model = Settlement
        fields = [
            "id",
            "trip_id",
            "receipt_id",
            "payer_user_id",
            "payee_user_id",
            "share_amount",
            "memo_code",
            "status",
            "verification_method",
            "verified_by_id",
            "requested_at",
            "paid_self_at",
            "confirmed_at",
            "due_at",
            "payment_channel",
            "proofs",
        ]

    def get_payment_channel(self, obj):
        channel = getattr(obj.receipt.trip, "payment_channel", None)
        if not channel:
            return None
        return {
            "provider": channel.provider,
            "payment_link": channel.payment_link,
            "account_holder_name": channel.account_holder_name,
        }


class SettlementPaySelfSerializer(serializers.Serializer):
    pass


class SettlementConfirmSerializer(serializers.Serializer):
    pass


class SettlementDisputeSerializer(serializers.Serializer):
    pass


class SettlementProofCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettlementProof
        fields = ["image_url"]