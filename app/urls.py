from django.urls import path
from .views import (
    HomeView,
    AboutPageView,
    CommissionCreateView,
    CommissionListView,
    CommissionDetailView,
    CommissionUpdateView,
    CommissionDeleteView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutPageView.as_view(), name='about'),
    # CRUD paths for the Commission table
    path('commissions/', CommissionListView.as_view(), name='commission-list'),
    path('commissions/create/', CommissionCreateView.as_view(), name='commission-create'),
    path('commissions/<int:pk>/', CommissionDetailView.as_view(), name='commission-detail'),
    path('commissions/<int:pk>/update/', CommissionUpdateView.as_view(), name='commission-update'),
    path('commissions/<int:pk>/delete/', CommissionDeleteView.as_view(), name='commission-delete'),
]
