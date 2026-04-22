from django.urls import path

from .views.reservation_views import (
    ReservationCreateAPIView, ReservationReleaseAPIView,
    ReservationConfrimAPIView
    )
from .views.cart_views import (
    AddToCartGenericView, CartListView,
    CartRemoveView, CartUpdateView
)

urlpatterns = [
    path('reservation/', ReservationCreateAPIView.as_view()),
    path('reservation/<int:reservation_id>/release/', ReservationReleaseAPIView.as_view()),
    path('reservation/<int:reservation_id>/confirm/', ReservationConfrimAPIView.as_view()),
    path('cart/add/', AddToCartGenericView.as_view()),
    path('cart/', CartListView.as_view()),
    path('cart/update/<int:reservation_id>/', CartUpdateView.as_view()),
    path('cart/remove/<int:reservation_id>/', CartRemoveView.as_view()),
]
