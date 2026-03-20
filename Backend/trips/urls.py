# trips/urls.py
from django.urls import path
from .views import (
    TripListCreateView,
    TripDetailView,
    TripJoinView,
    TripLeaveView,
    TripKickView,
    TripCloseView,
    TripMapPinListView,
)

urlpatterns = [
    path("trips/", TripListCreateView.as_view(), name="trip-list-create"),
    path("trips/<int:pk>/", TripDetailView.as_view(), name="trip-detail"),
    path("trips/<int:trip_id>/join/", TripJoinView.as_view(), name="trip-join"),
    path("trips/<int:trip_id>/leave/", TripLeaveView.as_view(), name="trip-leave"),
    path("trips/<int:trip_id>/kick/", TripKickView.as_view(), name="trip-kick"),
    path("trips/<int:trip_id>/close/", TripCloseView.as_view(), name="trip-close"),
path("trips/map-pins/", TripMapPinListView.as_view(), name="trip-map-pins"),
]