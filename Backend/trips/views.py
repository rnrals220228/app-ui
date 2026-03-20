# trips/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework import generics
from .models import Trip
from .serializers import (
    TripCreateSerializer,
    TripListSerializer,
    TripDetailSerializer,TripMapPinSerializer,
)
from .services import create_trip, join_trip, leave_trip, kick_participant, close_trip

class TripMapPinListView(generics.ListAPIView):
    serializer_class = TripMapPinSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        now = timezone.now()
        return (
            Trip.objects
            .filter(
                depart_time__gte=now,
                status__in=["OPEN", "FULL"],
            )
            .order_by("depart_time")
        )
class TripListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Trip.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TripCreateSerializer
        return TripListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trip = create_trip(
            user=request.user,
            validated_data=serializer.validated_data,
        )

        output = TripDetailSerializer(trip, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)
class TripDetailView(generics.RetrieveAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripDetailSerializer
    permission_classes = [IsAuthenticated]
class TripLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, trip_id):
        trip = Trip.objects.get(id=trip_id)
        trip = leave_trip(trip=trip, user=request.user)
        return Response(TripDetailSerializer(trip).data, status=status.HTTP_200_OK)
class TripKickView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, trip_id):
        target_user_id = request.data.get("user_id")
        if not target_user_id:
            return Response(
                {"detail": "user_id는 필수입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trip = Trip.objects.get(id=trip_id)
        trip = kick_participant(
            trip=trip,
            actor=request.user,
            target_user_id=target_user_id,
        )
        return Response(TripDetailSerializer(trip).data, status=status.HTTP_200_OK)
class TripCloseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, trip_id):
        trip = Trip.objects.get(id=trip_id)
        trip = close_trip(trip=trip, actor=request.user)
        return Response(TripDetailSerializer(trip).data, status=status.HTTP_200_OK)


# 아직 데이터 보관 DB에 연결안했고 없어지는것도 결제후로 처리 안되었음, 반경도 아직 없음