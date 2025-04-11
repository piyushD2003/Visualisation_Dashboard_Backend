from django.urls import path
from .views import DataAPIView, DashboardView

urlpatterns = [
    path('', DataAPIView.as_view(), name='dataentry'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
