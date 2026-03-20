# trips/serializers.py
from rest_framework import serializers
from .models import Trip, TripParticipant

class TripMapPinSerializer(serializers.ModelSerializer):
    trip_id = serializers.IntegerField(source="id", read_only=True)
    current_joined_count = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            "trip_id",
            "depart_name",
            "depart_lat",
            "depart_lng",
            "arrive_name",
            "arrive_lat",
            "arrive_lng",
            "depart_time",
            "status",
            "capacity",
            "current_joined_count",
        ]

    def get_current_joined_count(self, obj):
        return obj.trip_participants.filter(status="JOINED").count()
class TripCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            "depart_name",
            "depart_lat",
            "depart_lng",
            "arrive_name",
            "arrive_lat",
            "arrive_lng",
            "depart_time",
            "capacity",
            "estimated_fare",
        ]

    def validate(self, attrs):
        depart_name = attrs.get("depart_name")
        arrive_name = attrs.get("arrive_name")

        if depart_name == arrive_name:
            raise serializers.ValidationError("출발지와 도착지가 같을 수 없습니다.")

        return attrs

class TripParticipantSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = TripParticipant
        fields = [
            "id",
            "user_id",
            "role",
            "status",
            "confirmed_departure",
            "joined_at",
            "left_at",
        ]
class TripDetailSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    current_joined_count = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            "id",
            "creator_user",
            "leader_user",
            "depart_name",
            "depart_lat",
            "depart_lng",
            "arrive_name",
            "arrive_lat",
            "arrive_lng",
            "depart_time",
            "capacity",
            "status",
            "estimated_fare",
            "created_at",
            "current_joined_count",
            "participants",
        ]

    def get_participants(self, obj):
        qs = obj.trip_participants.filter(status="JOINED").select_related("user")
        return TripParticipantSerializer(qs, many=True).data

    def get_current_joined_count(self, obj):
        return obj.trip_participants.filter(status="JOINED").count()

class TripListSerializer(serializers.ModelSerializer):
    current_joined_count = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            "id",
            "depart_name",
            "arrive_name",
            "depart_time",
            "capacity",
            "status",
            "estimated_fare",
            "current_joined_count",
            "created_at",
        ]

    def get_current_joined_count(self, obj):
        return obj.trip_participants.filter(status="JOINED").count()