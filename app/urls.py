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
    path('commissions/', CommissionListView.as_view(), name='commission_list'),
    path('commission/', CommissionCreateView.as_view(), name='create_commission'),
    path('commissions/<int:pk>/', CommissionDetailView.as_view(), name='commission-detail'),
    path('commissions/<int:pk>/update/', CommissionUpdateView.as_view(), name='commission-update'),
    path('commissions/<int:pk>/delete/', CommissionDeleteView.as_view(), name='commission-delete'),
]
